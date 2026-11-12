"""Trust-boundary and real deterministic HTTP workflow checks; no Azure calls."""
import base64
import io
import json
import os
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile
from deployment.learning import web_api
from deployment.learning.build_package import build


def headers(tenant='tenant-a', subject='user-a', roles=('Forecast.User',)):
    claims = [{'typ': 'tid', 'val': tenant}, {'typ': 'oid', 'val': subject}]
    claims += [{'typ': 'roles', 'val': role} for role in roles]
    return base64.b64encode(json.dumps({'auth_typ': 'aad', 'claims': claims}).encode()).decode()


class LearningWebTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.env = patch.dict(os.environ, {'WEBSITE_INSTANCE_ID': 'test-instance',
            'FORECAST_WEB_TENANT_ID': 'tenant-a', 'ENABLE_LLM': 'false',
            'FORECAST_WEB_STATE_BACKEND': 'sqlite', 'FORECAST_STATE_DIR': self.temp.name})
        self.env.start()
        self.addCleanup(self.env.stop)
        web_api.core.cache_clear()
        self.addCleanup(web_api.core.cache_clear)

    def call(self, path='/ask', body=None, principal=None, method='POST', raw=None, **extra):
        data = json.dumps(body or {'session_id': 'test-session', 'request_id': 'test-request',
                                  'message': 'Analyze forecast performance for P0001 in North.'}).encode() if raw is None else raw
        environ = {'PATH_INFO': path, 'REQUEST_METHOD': method,
            'CONTENT_TYPE': 'application/json', 'CONTENT_LENGTH': str(len(data)),
            'wsgi.input': io.BytesIO(data), 'HTTP_HOST': 'lab.azurewebsites.net',
            'HTTP_X_MS_CLIENT_PRINCIPAL': principal if principal is not None else headers()}
        environ.update(extra)
        statuses = []
        result = b''.join(web_api.application(environ, lambda status, response_headers: statuses.append(status)))
        return int(statuses[0].split()[0]), result

    def test_spoofed_principal_outside_platform_is_denied(self):
        with patch.dict(os.environ, {'WEBSITE_INSTANCE_ID': ''}):
            self.assertEqual(self.call()[0], 403)

    def test_invalid_identity_and_role_are_denied(self):
        for principal in ('garbage', '', headers(tenant='other'), headers(roles=()),
                          base64.b64encode(b'{"claims":null}').decode()):
            self.assertEqual(self.call(principal=principal)[0], 403)

    def test_body_cannot_set_identity(self):
        self.assertEqual(self.call(body={'session_id':'a','request_id':'b','message':'hello',
                                        'principal':{'subject':'admin'}})[0], 400)

    def test_cross_origin_and_malformed_requests(self):
        self.assertEqual(self.call(HTTP_ORIGIN='https://evil.example')[0], 403)
        self.assertEqual(self.call(raw=b'{bad')[0], 400)
        self.assertEqual(self.call(CONTENT_LENGTH='20000')[0], 413)
        self.assertEqual(self.call(CONTENT_TYPE='text/plain')[0], 415)

    def test_real_analysis_followup_replay_restart_and_owner_isolation(self):
        status, first = self.call()
        self.assertEqual(status, 200)
        self.assertIn(b'88.89', first)
        self.assertEqual(self.call()[1], first)  # Same request is deduplicated.
        web_api.core.cache_clear()  # Reopen persisted state, as after process restart.
        followup = {'session_id':'test-session','request_id':'revenue','message':'What about revenue?'}
        status, answer = self.call(body=followup)
        self.assertEqual(status, 200)
        self.assertIn(b'12825', answer)
        status, other = self.call(body=followup, principal=headers(subject='other-user'))
        self.assertEqual(status, 403)
        self.assertNotIn(b'12825', other)

    def test_public_health_does_not_claim_storage_readiness(self):
        status, body = self.call('/health', method='GET', principal='')
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)['status'], 'alive')

    def test_package_excludes_state_and_secrets_and_has_http_entrypoint(self):
        with ZipFile(build(self.temp.name + '/app.zip')) as archive:
            names = archive.namelist()
            self.assertIn('deployment/learning/web_api.py', names)
            self.assertIn('deployment/learning/index.html', names)
            self.assertFalse(any('.env' in name or '.sqlite' in name or name.startswith('tests/') for name in names))
            self.assertNotIn(b'microsoft-agents', archive.read('requirements.txt'))


if __name__ == '__main__':
    unittest.main()
