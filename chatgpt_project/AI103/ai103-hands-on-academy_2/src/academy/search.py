# Purpose: Implement Azure Search ingestion and retrieval
# Learn: Inspect index fields, vector dimensions, query modes and tenant filters.
# Run: Imported by lesson code; do not run this file directly. Follow the importing lesson in MASTER_GUIDE.md.

"""A small REST-based Azure AI Search index with real model embeddings."""
from urllib.parse import quote
from .common import env,read
from .cloud import request,embed
VERSION='2024-07-01'
def call(method,path,body=None):
    return request(method,env('SEARCH_ENDPOINT').rstrip('/')+'/'+path+'?api-version='+VERSION,
                   headers={'api-key':env('SEARCH_ADMIN_KEY'),'Content-Type':'application/json'},
                   body=body,safe_retry=method=='GET').json()
def index_name():
    return quote(env('SEARCH_INDEX','ai103-policies-v1'),safe='')
def ingest():
    """Index the supplied five-document synthetic corpus."""
    return ingest_rows(read('data/policies.json'))

def ingest_rows(rows):
    """Embed records and upload them to an explicitly named learning index."""
    if not rows:
        raise ValueError('No records to ingest')
    vectors=embed([r['text'] for r in rows])
    dims=len(vectors[0])
    fields=[{'name':'id','type':'Edm.String','key':True},
            {'name':'text','type':'Edm.String','searchable':True},
            {'name':'tenant','type':'Edm.String','filterable':True},
            {'name':'kind','type':'Edm.String','filterable':True},
            {'name':'vector','type':'Collection(Edm.Single)','searchable':True,
             'dimensions':dims,'vectorSearchProfile':'vp'}]
    call('PUT','indexes/'+index_name(),{'name':env('SEARCH_INDEX','ai103-policies-v1'),'fields':fields,
        'vectorSearch':{'algorithms':[{'name':'hnsw','kind':'hnsw'}],
                        'profiles':[{'name':'vp','algorithm':'hnsw'}]},
        'semantic':{'configurations':[{'name':'sem','prioritizedFields':{'prioritizedContentFields':[{'fieldName':'text'}]}}]}})
    result=call('POST','indexes/'+index_name()+'/docs/index',
                {'value':[{'@search.action':'mergeOrUpload',**r,'vector':v} for r,v in zip(rows,vectors)]})
    failures=[r['key'] for r in result['value'] if not r['status']]
    if failures:
        raise RuntimeError(f'Indexing failed for {len(failures)} records')
    return {'indexed':len(rows),'dimensions':dims,'index':env('SEARCH_INDEX','ai103-policies-v1')}
def search(question,tenant='retail',mode='hybrid'):
    """Apply trusted tenant scope and the selected lexical/vector/reranking method."""
    if mode not in ('keyword','vector','hybrid','semantic'):
        raise ValueError('Unknown search mode')
    # Caller supplies tenant from validated identity; never from model-generated arguments.
    body={'top':3,'select':'id,text,tenant,kind','filter':"tenant eq '"+tenant.replace("'","''")+"'"}
    if mode!='vector':
        body['search']=question
    if mode!='keyword':
        body['vectorQueries']=[{'kind':'vector','vector':embed([question])[0],'fields':'vector','k':50}]
    if mode=='semantic':
        body.update(queryType='semantic',semanticConfiguration='sem')
    return call('POST','indexes/'+index_name()+'/docs/search',body)['value']
