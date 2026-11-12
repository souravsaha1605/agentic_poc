"""App Service Easy Auth boundary for the synthetic forecast learning deployment.

Only deploy behind required App Service authentication. The platform validates
JWTs and replaces X-MS-CLIENT-PRINCIPAL; this module does not validate JWTs.
Never expose this WSGI process directly to an untrusted reverse proxy.
"""
import base64
import binascii
import json
import logging
import os
import time
import uuid
from functools import lru_cache

from contracts import Principal, TurnRequest
from runtime import create_core

LOG = logging.getLogger('forecast.http')


def authenticated_principal(environ):
    if not os.getenv('WEBSITE_INSTANCE_ID') or not os.getenv('FORECAST_WEB_TENANT_ID'):
        raise PermissionError('App Service identity boundary is required')
    encoded = environ.get('HTTP_X_MS_CLIENT_PRINCIPAL', '')
    if not encoded or len(encoded) > 24000:
        raise PermissionError('Missing principal')
    try:
        data = json.loads(base64.b64decode(encoded, validate=True))
        if data.get('auth_typ') != 'aad':
            raise ValueError('Unsupported provider')
        claims = data['claims']
        if not isinstance(claims, list):
            raise ValueError('Invalid claims')
        def values(*names):
            return {c['val'] for c in claims if c.get('typ') in names}
        tenants = values('tid', 'http://schemas.microsoft.com/identity/claims/tenantid')
        subjects = values('oid', 'http://schemas.microsoft.com/identity/claims/objectidentifier')
        roles = values('roles', 'http://schemas.microsoft.com/ws/2008/06/identity/claims/role')
        if tenants != {os.environ['FORECAST_WEB_TENANT_ID']} or len(subjects) != 1 or 'Forecast.User' not in roles:
            raise ValueError('Tenant, subject or role denied')
        # The grant is deliberately limited to this synthetic lab, never enterprise data.
        return Principal(tenant=next(iter(tenants)), subject=next(iter(subjects)),
                         regions=('*',), products=('*',), categories=('*',))
    except (ValueError, KeyError, TypeError, AttributeError, binascii.Error) as error:
        raise PermissionError('Invalid principal or role') from error


@lru_cache(maxsize=1)
def core():
    if os.getenv('ENABLE_LLM', 'false').lower() != 'false':
        raise RuntimeError('The learning HTTP deployment requires ENABLE_LLM=false')
    backend = os.getenv('FORECAST_WEB_STATE_BACKEND', 'azure')
    if backend not in ('azure', 'sqlite'):
        raise RuntimeError('Unsupported learning state backend')
    return create_core('lab', state_backend=backend)


def application(environ, start_response):
    started = time.monotonic()
    trace_id = uuid.uuid4().hex
    def respond(status, value, content_type='application/json'):
        body = (json.dumps(value) if content_type == 'application/json' else value).encode()
        LOG.warning(json.dumps({'event': 'http.completed', 'trace_id': trace_id,
                                'status': int(status.split()[0]),
                                'duration_ms': round((time.monotonic()-started)*1000)}))
        start_response(status, [('Content-Type', content_type), ('Content-Length', str(len(body))),
                               ('Cache-Control', 'no-store'), ('X-Content-Type-Options', 'nosniff'),
                               ('X-Trace-Id', trace_id)])
        return [body]
    path = environ.get('PATH_INFO', '')
    method = environ.get('REQUEST_METHOD', '')
    if path == '/health' and method == 'GET':
        return respond('200 OK', {'status': 'alive', 'data': 'synthetic-lab', 'llm': False})
    try:
        principal = authenticated_principal(environ)
    except PermissionError:
        return respond('403 Forbidden', {'error': 'Sign in with an assigned Forecast.User identity'})
    if path == '/' and method == 'GET':
        from pathlib import Path
        return respond('200 OK', Path(__file__).with_name('index.html').read_text(), 'text/html; charset=utf-8')
    if path == '/ready' and method == 'GET':
        try:
            core()  # Application initialization; /ask verifies actual state writes and reads.
            return respond('200 OK', {'status': 'initialized', 'functional_check': 'POST /ask'})
        except Exception:
            return respond('503 Service Unavailable', {'error': 'Check managed identity and Blob RBAC', 'trace_id': trace_id})
    if path != '/ask' or method != 'POST':
        return respond('404 Not Found', {'error': 'not found'})
    if environ.get('CONTENT_TYPE', '').split(';')[0] != 'application/json':
        return respond('415 Unsupported Media Type', {'error': 'application/json required'})
    # Browser requests must originate at this site. Non-browser token callers omit Origin.
    origin = environ.get('HTTP_ORIGIN')
    if origin and origin != 'https://' + environ.get('HTTP_HOST', ''):
        return respond('403 Forbidden', {'error': 'cross-origin request denied'})
    try:
        length = int(environ.get('CONTENT_LENGTH', '0'))
        if not 0 < length <= 12000:
            return respond('413 Content Too Large', {'error': 'request must be 1..12000 bytes'})
        raw = environ['wsgi.input'].read(length)
        if len(raw) != length:
            raise ValueError('incomplete body')
        request = TurnRequest.model_validate(json.loads(raw))
        if request.channel != 'development':
            raise ValueError('This endpoint is not the Teams channel')
    except (ValueError, KeyError, TypeError):
        return respond('400 Bad Request', {'error': 'Expected message, session_id and unique request_id; no identity fields'})
    try:
        result = core().handle(principal, request.model_dump(mode='json'))
        return respond('200 OK', {'data': 'synthetic-lab', 'result': result})
    except PermissionError:
        return respond('403 Forbidden', {'error': 'case access denied'})
    except ValueError:
        return respond('409 Conflict', {'error': 'Invalid state or request conflict; inspect the request and case version'})
    except Exception:
        # Do not log request bodies, principal headers, tokens or business records.
        return respond('503 Service Unavailable', {'error': 'Service unavailable; check startup and storage RBAC', 'trace_id': trace_id})
