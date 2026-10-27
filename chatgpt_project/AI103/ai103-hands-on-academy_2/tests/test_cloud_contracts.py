# Purpose: Protect behavior with automated regression tests
# Learn: Check https required, write is not retried, retry after not overridden, failures do not expose body.
# Run: From project root: PYTHONPATH=src python -m unittest discover -s tests -v. Service doubles are not live Azure tests; test names describe the assertions.

"""Contract/failure checks with test doubles; these are NOT live Azure validation."""
import sys,types,unittest
from unittest.mock import patch
from academy.cloud import request
class CloudContractTests(unittest.TestCase):
    def test_https_required(self):
        fake=types.SimpleNamespace(request=lambda *a,**k:None,RequestException=Exception)
        with patch.dict(sys.modules,{'requests':fake}):
            with self.assertRaises(ValueError):
                request('GET','http://untrusted.test')
    def test_write_is_not_retried(self):
        calls=[]
        def call(*a,**k):
            calls.append(k)
            return types.SimpleNamespace(status_code=503,headers={})
        fake=types.SimpleNamespace(request=call,RequestException=OSError)
        with patch.dict(sys.modules,{'requests':fake}):
            with self.assertRaises(RuntimeError):
                request('POST','https://example.test',body={'x':1})
        self.assertEqual(len(calls),1)
        self.assertFalse(calls[0]['allow_redirects'])
    def test_retry_after_not_overridden(self):
        calls=[]
        def call(*a,**k):
            calls.append(1)
            return types.SimpleNamespace(status_code=429,headers={'Retry-After':'120'})
        with patch.dict(sys.modules,{'requests':types.SimpleNamespace(request=call,RequestException=OSError)}):
            with self.assertRaises(RuntimeError):
                request('GET','https://example.test',safe_retry=True)
        self.assertEqual(len(calls),1)
    def test_failures_do_not_expose_body(self):
        fake=types.SimpleNamespace(request=lambda *a,**k:types.SimpleNamespace(status_code=403,headers={},text='secret-value'),RequestException=OSError)
        with patch.dict(sys.modules,{'requests':fake}):
            with self.assertRaises(RuntimeError) as ctx:
                request('GET','https://example.test')
        self.assertNotIn('secret-value',str(ctx.exception))
if __name__=='__main__':
    unittest.main()
