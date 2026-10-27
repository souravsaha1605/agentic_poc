# Purpose: Protect behavior with automated regression tests
# Learn: Check unknown role denied before backend, cross tenant approval denied, same user other tenant cannot execute, legacy ledger fails closed, role change does not reuse cache and related cases.
# Run: From project root: PYTHONPATH=src python -m unittest discover -s tests -v. Service doubles are not live Azure tests; test names describe the assertions.

"""Regression checks for tenant authorization, bootstrap, and notebook cleanup."""
import contextlib
import io
import json
import os
from pathlib import Path
import runpy
import tempfile
import types
import unittest
import zipfile
from unittest.mock import patch
from academy.domain import ALICE, SUPERVISOR, Ledger, Principal, TTLCache, execute_tool
from academy import notebook

ROOT = Path(__file__).resolve().parents[1]

class FinalReviewTests(unittest.TestCase):
    def test_non_ascii_invalid_token_is_unauthorized(self):
        from academy.api import application
        statuses = []
        with patch.dict(os.environ, {'API_DEMO_TOKEN':'test'}):
            application({'PATH_INFO':'/ask', 'REQUEST_METHOD':'POST',
                         'HTTP_AUTHORIZATION':'Bearer invalid-é'},
                        lambda status, headers: statuses.append(status))
        self.assertEqual(statuses, ['401 Unauthorized'])

    def test_unknown_role_denied_before_backend(self):
        with self.assertRaises(PermissionError):
            execute_tool('search_policy', {'query': 'returns'}, Principal('x', 'unknown'),
                         lambda *a, **k: self.fail('Backend must not be reached'))

    def test_cross_tenant_approval_denied(self):
        ledger = Ledger(':memory:')
        try:
            ledger.create('r', 'ORD-1001', ALICE)
            with self.assertRaises(PermissionError):
                ledger.decide('r', Principal('reviewer', 'supervisor', 'partner'), True)
            self.assertEqual(ledger.get('r')['state'], 'pending')
        finally:
            ledger.close()

    def test_same_user_other_tenant_cannot_execute(self):
        ledger = Ledger(':memory:')
        try:
            ledger.create('r', 'ORD-1001', ALICE)
            ledger.decide('r', SUPERVISOR, True)
            with self.assertRaises(PermissionError):
                ledger.execute('r', Principal('alice', 'customer', 'partner'))
            self.assertEqual(ledger.db.execute('SELECT COUNT(*) FROM effects').fetchone()[0], 0)
            self.assertEqual(ledger.execute('r', ALICE)['state'], 'executed')
        finally:
            ledger.close()

    def test_legacy_ledger_fails_closed(self):
        ledger = Ledger(':memory:')
        try:
            ledger.create('r', 'ORD-1001', ALICE)
            payload = json.loads(ledger.db.execute('SELECT payload FROM refunds').fetchone()[0])
            payload.pop('tenant')
            with ledger.db:
                ledger.db.execute('UPDATE refunds SET payload=?', (json.dumps(payload),))
            with self.assertRaises(PermissionError):
                ledger.decide('r', SUPERVISOR, True)
        finally:
            ledger.close()

    def test_role_change_does_not_reuse_cache(self):
        cache = TTLCache()
        cache.put(cache.key(ALICE, 'q', 'v1'), 'private', 60)
        self.assertIsNone(cache.get(cache.key(Principal('alice', 'supervisor'), 'q', 'v1')))

    def test_volume_paths(self):
        for path in ('/tmp/x', '/Volumes/c', '/Volumes/c/s/v/../../tmp', '/Volumes/YOUR_CATALOG/s/v'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                notebook.output_directory(path)
        self.assertEqual(str(notebook.output_directory('/Volumes/c/s/v/results')), '/Volumes/c/s/v/results')

    def test_notebook_restores_runtime_and_clears_credentials(self):
        # Stub only lesson execution: this tests launcher success AND failure cleanup.
        for failure in (False, True):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as tmp:
                values = {'live':'false', 'variant':'default', 'config_json':'{}',
                          'output_root':'/Volumes/c/s/v', 'question':'returns', 'input_file':''}
                dbutils = types.SimpleNamespace(widgets=types.SimpleNamespace(get=values.__getitem__))
                runtime_env = {'ACADEMY_OUTPUT_DIR':'previous', 'ACADEMY_SKIP_DOTENV':'false',
                               'AZURE_OPENAI_API_KEY':'must-be-cleared'}
                with patch.dict(os.environ, runtime_env), patch.object(notebook, 'output_directory', return_value=Path(tmp)), \
                     patch.object(notebook.runpy, 'run_path', side_effect=RuntimeError('fixture') if failure else None), \
                     contextlib.redirect_stdout(io.StringIO()):
                    if failure:
                        with self.assertRaises(RuntimeError):
                            notebook.run(dbutils, ROOT, 'labs/00_environment_and_project_tour')
                    else:
                        notebook.run(dbutils, ROOT, 'labs/00_environment_and_project_tour')
                    self.assertEqual(os.environ['ACADEMY_OUTPUT_DIR'], 'previous')
                    self.assertEqual(os.environ['ACADEMY_SKIP_DOTENV'], 'false')
                    self.assertNotIn('AZURE_OPENAI_API_KEY', os.environ)
                    status = json.loads(next(Path(tmp).rglob('run_status.json')).read_text())
                    self.assertEqual(status['status'], 'failed' if failure else 'completed')

    def test_bootstrap_extracts_and_rejects_traversal(self):
        # Replace filesystem boundaries only; execute the actual bootstrap unchanged.
        for unsafe in (False, True):
            with self.subTest(unsafe=unsafe), tempfile.TemporaryDirectory() as tmp:
                base = Path(tmp)
                archive = base/'course.zip'
                with zipfile.ZipFile(archive, 'w') as z:
                    for name in ('notebook.py', 'common.py'):
                        z.writestr('ai103-hands-on-academy/src/academy/'+name, '# fixture')
                    if unsafe:
                        z.writestr('../escape.py', '# forbidden')
                output = types.SimpleNamespace(parts=('/', 'Volumes', 'c', 's', 'v'), mkdir=lambda **k: None)
                class Volume:
                    parts = output.parts
                    def __str__(self): return '/Volumes/c/s/v'
                    def mkdir(self, **kwargs): pass
                def boundary(value):
                    if str(value) == '/local_disk0/tmp/ai103-course': return base/'driver'
                    if str(value) == '/Volumes/c/s/v': return Volume()
                    return Path(value)
                values = {'zip_path':str(archive), 'output_root':'/Volumes/c/s/v'}
                mock = types.SimpleNamespace(widgets=types.SimpleNamespace(text=lambda *a: None, get=values.__getitem__))
                with patch('pathlib.Path', side_effect=boundary), contextlib.redirect_stdout(io.StringIO()):
                    if unsafe:
                        with self.assertRaises(ValueError):
                            runpy.run_path(str(ROOT/'databricks/00_BOOTSTRAP.py'), init_globals={'dbutils':mock})
                    else:
                        runpy.run_path(str(ROOT/'databricks/00_BOOTSTRAP.py'), init_globals={'dbutils':mock})
                self.assertFalse((base/'escape.py').exists())
                if not unsafe:
                    self.assertTrue((base/'driver/ai103-hands-on-academy/src/academy/common.py').is_file())

if __name__ == '__main__':
    unittest.main()
