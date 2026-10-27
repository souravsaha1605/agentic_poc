# Purpose: Enforce deterministic business and authorization rules
# Learn: Trace tenant/owner checks, allowed roles, ledger transitions, idempotency and role-aware cache keys.
# Run: Imported by lesson code; do not run this file directly. Follow the importing lesson in MASTER_GUIDE.md.

"""Deterministic rules are the authority for access and business actions."""
import hashlib
import json
import math
import re
import sqlite3
import time
from dataclasses import dataclass
from .common import read

@dataclass(frozen=True)
class Principal:
    user: str
    role: str
    tenant: str = 'retail'

# Local fixtures stand in for VALIDATED authentication claims, never user prompt text.
ALICE=Principal('alice','customer')
SUPERVISOR=Principal('supervisor-1','supervisor')

def tokens(text):
    stop={'the','is','what','a','an','to','of','and','i','my','for','in','how','can'}
    return {w.rstrip('s') for w in re.findall(r'[a-z0-9]+',text.lower()) if w not in stop}

def retrieve(question, principal=ALICE, k=3):
    """Retrieve only documents belonging to the trusted principal tenant."""
    rows=[r for r in read('data/policies.json') if r['tenant'] == principal.tenant]
    rows.sort(key=lambda r:len(tokens(question)&tokens(r['id']+' '+r['text'])),reverse=True)
    return [r for r in rows if tokens(question)&tokens(r['id']+' '+r['text'])][:k]

def redact(text):
    # Demo recognizer, not a complete PII detector. Lab 06 uses Azure AI Language.
    """Mask email addresses for a small local demo; not a complete PII system."""
    return re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}','[EMAIL]',text)

def local_guard(text):
    """Reject empty/oversized input and flag a deliberately small attack baseline."""
    if not text.strip() or len(text)>8000:
        raise ValueError('Input length must be 1..8000')
    return any(p in text.lower() for p in ('ignore previous','reveal secret','system prompt'))

def validate_answer(obj, source_ids):
    """Validate output shape and known source IDs, not factual entailment."""
    if not isinstance(obj,dict) or set(obj) != {'answer','sources','uncertain'}:
        raise ValueError('Wrong fields')
    if not isinstance(obj['answer'],str) or not isinstance(obj['uncertain'],bool):
        raise ValueError('Wrong field type')
    if not isinstance(obj['sources'],list) or not all(isinstance(s,str) and s in source_ids for s in obj['sources']):
        raise ValueError('Unknown source')
    return obj  # Valid references do NOT prove claim-level groundedness.

def order_for(order_id, principal):
    """Enforce both owner and tenant before returning an order."""
    order=read('data/orders.json').get(order_id)
    if order is None or order['user'] != principal.user or order['tenant'] != principal.tenant:
        raise PermissionError('Order unavailable to this user')
    return order

def eligibility(order_id, principal):
    """Compute business eligibility from trusted records, not model judgment."""
    order=order_for(order_id,principal)
    return {'order_id':order_id,'eligible':order['days']<=30 and order['unused'] and order['receipt'],
            'amount_paise':order['amount_paise'],'approval_required':order['amount_paise']>100000}

def allowed_tools(principal):
    """Derive tool permissions from trusted role state."""
    return {'customer': ['order_status', 'search_policy'],
            'supervisor': ['search_policy']}.get(principal.role, [])

def execute_tool(name, arguments, principal, policy_search=None):
    """Validate permission and arguments before invoking an allowlisted tool."""
    if name not in allowed_tools(principal):
        raise PermissionError('Tool denied')
    if not isinstance(arguments,dict):
        raise ValueError('Arguments must be an object')
    if name=='order_status':
        if set(arguments)!={'order_id'} or not isinstance(arguments['order_id'],str):
            raise ValueError('Invalid order arguments')
        return eligibility(arguments['order_id'],principal)
    if set(arguments)!={'query'} or not isinstance(arguments['query'],str) or len(arguments['query'])>1000:
        raise ValueError('Invalid search arguments')
    # Authorization and argument validation happen BEFORE calling an external store.
    if policy_search is not None:
        return policy_search(arguments['query'], tenant=principal.tenant)
    return retrieve(arguments['query'],principal)

TOOL_SCHEMAS=[{'type':'function','function':{'name':'order_status','description':'Read eligibility for an order owned by the signed-in user.',
 'parameters':{'type':'object','properties':{'order_id':{'type':'string'}},'required':['order_id'],'additionalProperties':False}}},
 {'type':'function','function':{'name':'search_policy','description':'Find permitted retail policy evidence.',
 'parameters':{'type':'object','properties':{'query':{'type':'string'}},'required':['query'],'additionalProperties':False}}}]

class Ledger:
    """SQLite local teaching ledger: approval + deduplication + atomic simulated effects."""
    def __init__(self,path):
        self.db=sqlite3.connect(path)
        self.db.execute('CREATE TABLE IF NOT EXISTS refunds (id TEXT PRIMARY KEY, payload TEXT, state TEXT, expires REAL, approver TEXT)')
        self.db.execute('CREATE TABLE IF NOT EXISTS effects (id TEXT PRIMARY KEY, amount INTEGER)')
    def create(self,key,order_id,principal,ttl=3600):
        check=eligibility(order_id,principal)
        if not check['eligible']:
            raise ValueError('Ineligible order')
        payload=json.dumps({'user':principal.user,'tenant':principal.tenant,**check},sort_keys=True)
        state='pending' if check['approval_required'] else 'approved'
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            old=self.db.execute('SELECT payload FROM refunds WHERE id=?',(key,)).fetchone()
            if old and old[0]!=payload:
                raise ValueError('Idempotency key reused for a different request')
            self.db.execute('INSERT OR IGNORE INTO refunds VALUES (?,?,?,?,?)',(key,payload,state,time.time()+ttl,None))
        return self.get(key)
    def get(self,key):
        r=self.db.execute('SELECT payload,state,expires,approver FROM refunds WHERE id=?',(key,)).fetchone()
        if not r:
            raise KeyError('Unknown request')
        return {'id':key,**json.loads(r[0]),'state':r[1],'expires':r[2],'approver':r[3]}
    def decide(self, key, principal, approve):
        """Atomically check the current state before recording a supervisor decision."""
        if principal.role != 'supervisor':
            raise PermissionError('Supervisor role required')
        if not isinstance(approve, bool):
            raise ValueError('Approval must be a boolean, never a model-generated string')
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            request = self.get(key)
            # Missing tenant on an older teaching ledger also fails closed.
            if request.get('tenant') != principal.tenant:
                raise PermissionError('Same tenant required; recreate legacy teaching requests')
            if request['user'] == principal.user:
                raise PermissionError('Self approval denied')
            if request['state'] != 'pending':
                raise ValueError('Not pending')
            state = ('approved' if approve else 'rejected') if time.time() < request['expires'] else 'expired'
            self.db.execute('UPDATE refunds SET state=?,approver=? WHERE id=?', (state, principal.user, key))
        return self.get(key)
    def execute(self,key,principal):
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            r=self.get(key)
            if r['user']!=principal.user or r.get('tenant')!=principal.tenant:
                raise PermissionError('Owner and tenant required')
            if r['state']=='executed':
                return r
            if r['state']!='approved' or time.time()>=r['expires']:
                raise PermissionError('Valid approval required')
            self.db.execute('INSERT OR IGNORE INTO effects VALUES (?,?)',(key,r['amount_paise']))
            self.db.execute('UPDATE refunds SET state=? WHERE id=?',('executed',key))
        return self.get(key)
    def close(self):
        self.db.close()

class TTLCache:
    def __init__(self):
        self.values={}
    def key(self,principal,query,version):
        return (principal.tenant,principal.user,principal.role,version,query)
    def put(self,key,value,ttl):
        self.values[key]=(time.monotonic()+ttl,value)
    def get(self,key):
        item=self.values.get(key)
        return item[1] if item and item[0]>time.monotonic() else None

def cosine(a,b):
    """Compare vector direction; reject incompatible embedding dimensions."""
    if len(a)!=len(b):
        raise ValueError('Embedding dimension mismatch')
    den=math.sqrt(sum(x*x for x in a)*sum(x*x for x in b))
    return sum(x*y for x,y in zip(a,b))/den if den else 0

def chunk(text,size=50,overlap=10):
    """Split text with word overlap; this teaching splitter is not a tokenizer."""
    if not 0<=overlap<size:
        raise ValueError('Require 0 <= overlap < size')
    words=text.split()
    return [' '.join(words[i:i+size]) for i in range(0,len(words),size-overlap)]
