# Purpose: Protect behavior with automated regression tests
# Learn: Check cross user order denied, unknown tool denied, extra argument denied, tenant retrieval, wrong tenant evidence denied and related cases.
# Run: From project root: PYTHONPATH=src python -m unittest discover -s tests -v. Service doubles are not live Azure tests; test names describe the assertions.

import io,json,os,time,unittest
from unittest.mock import patch
from academy.domain import ALICE,SUPERVISOR,Principal,Ledger,TTLCache,retrieve,execute_tool,validate_answer,cosine,chunk
from academy.memory import Memory
from academy.flows import rag
from academy.api import application

class BoundaryTests(unittest.TestCase):
    def test_cross_user_order_denied(self):
        with self.assertRaises(PermissionError):
            execute_tool('order_status',{'order_id':'ORD-1002'},ALICE)
    def test_unknown_tool_denied(self):
        with self.assertRaises(PermissionError):
            execute_tool('delete_all',{},ALICE)
    def test_extra_argument_denied(self):
        with self.assertRaises(ValueError):
            execute_tool('order_status',{'order_id':'ORD-1001','user':'bob'},ALICE)
    def test_tenant_retrieval(self):
        self.assertFalse(any(r['tenant']=='partner' for r in retrieve('wholesale discount',ALICE)))
    def test_wrong_tenant_evidence_denied(self):
        with self.assertRaises(PermissionError):
            rag('discount',evidence=[{'id':'x','text':'private','tenant':'partner'}])
    def test_abstention(self):
        self.assertTrue(rag('astronomy quantum neutrinos')['uncertain'])
    def test_unknown_source_denied(self):
        with self.assertRaises(ValueError):
            validate_answer({'answer':'x','sources':['invented'],'uncertain':False},{'valid'})
    def test_pending_cannot_execute(self):
        db=Ledger(':memory:')
        db.create('r','ORD-1001',ALICE)
        with self.assertRaises(PermissionError):
            db.execute('r',ALICE)
        db.close()
    def test_unauthorized_approval(self):
        db=Ledger(':memory:')
        db.create('r','ORD-1001',ALICE)
        with self.assertRaises(PermissionError):
            db.decide('r',ALICE,True)
        with self.assertRaises(PermissionError):
            db.decide('r',Principal('alice','supervisor'),True)
        db.close()
    def test_rejected_cannot_execute(self):
        db=Ledger(':memory:')
        db.create('r','ORD-1001',ALICE)
        db.decide('r',SUPERVISOR,False)
        with self.assertRaises(PermissionError):
            db.execute('r',ALICE)
        db.close()
    def test_expired_approval(self):
        db=Ledger(':memory:')
        db.create('r','ORD-1001',ALICE,ttl=-1)
        self.assertEqual(db.decide('r',SUPERVISOR,True)['state'],'expired')
        with self.assertRaises(PermissionError):
            db.execute('r',ALICE)
        db.close()
    def test_duplicate_effect(self):
        db=Ledger(':memory:')
        db.create('r','ORD-1001',ALICE)
        db.decide('r',SUPERVISOR,True)
        db.execute('r',ALICE)
        db.execute('r',ALICE)
        self.assertEqual(db.db.execute('SELECT COUNT(*) FROM effects').fetchone()[0],1)
        db.close()
    def test_conflicting_idempotency_payload(self):
        db=Ledger(':memory:')
        db.create('r','ORD-1001',ALICE)
        with patch('academy.domain.eligibility',return_value={'order_id':'ORD-OTHER','eligible':True,'amount_paise':50000,'approval_required':False}):
            with self.assertRaises(ValueError):
                db.create('r','ORD-OTHER',ALICE)
        db.close()
    def test_memory_isolation_and_expiry(self):
        db=Memory(':memory:')
        db.put('alice','s',['x'])
        self.assertEqual(db.get('bob','s'),[])
        db.put('alice','s',['x'],ttl=-1)
        self.assertEqual(db.get('alice','s'),[])
        db.close()
    def test_cache_scope_and_version(self):
        c=TTLCache()
        k=c.key(ALICE,'q','v1')
        c.put(k,'sensitive',60)
        self.assertIsNone(c.get(c.key(Principal('bob','customer'),'q','v1')))
        self.assertIsNone(c.get(c.key(ALICE,'q','v2')))
    def test_chunk_and_vector_errors(self):
        with self.assertRaises(ValueError):
            chunk('a b',2,2)
        with self.assertRaises(ValueError):
            cosine([1,2],[1])
    def test_api_requires_token(self):
        captured=[]
        with patch.dict(os.environ,{'API_DEMO_TOKEN':'test-only'}):
            body=application({'PATH_INFO':'/ask','REQUEST_METHOD':'POST','HTTP_AUTHORIZATION':'','wsgi.input':io.BytesIO(b'{}')},lambda s,h:captured.append(s))
        self.assertEqual(captured[0],'401 Unauthorized')
    def test_api_valid_request(self):
        captured=[]
        payload=json.dumps({'question':'return policy'}).encode()
        with patch.dict(os.environ,{'API_DEMO_TOKEN':'test-only','API_LIVE':'false'}):
            body=application({'PATH_INFO':'/ask','REQUEST_METHOD':'POST','HTTP_AUTHORIZATION':'Bearer test-only',
              'CONTENT_LENGTH':str(len(payload)),'wsgi.input':io.BytesIO(payload)},lambda s,h:captured.append(s))
        self.assertEqual(captured[0],'200 OK')
        self.assertIn('30 days',json.loads(body[0])['answer'])
if __name__=='__main__':
    unittest.main()
