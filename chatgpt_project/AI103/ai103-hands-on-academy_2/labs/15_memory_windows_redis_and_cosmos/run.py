# Purpose: Persist and bound conversation memory
# Learn: Compare local windows with Redis/Cosmos persistence, expiry and user/session separation.
# Run: Import databricks/labs/15_memory_windows_redis_and_cosmos.py as a Databricks source notebook. Start live=false; read labs/15_memory_windows_redis_and_cosmos/RUNBOOK.md.

"""Lab 15: Memory windows Redis and Cosmos. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import args,save,env
from academy.memory import Memory,window
opts=args('Demonstrate scoped memory or use Redis/Cosmos')
messages=[{'role':'user','content':'My order is ORD-1001.'},{'role':'assistant','content':'I will check it.'}]
if opts.live and opts.variant=='redis':
    import redis,json
    db=redis.Redis.from_url(env('REDIS_URL'),decode_responses=True)
    db.set('ai103:alice:session-1',json.dumps(messages),ex=60)
    result={'stored_messages':json.loads(db.get('ai103:alice:session-1')),'ttl':db.ttl('ai103:alice:session-1')}
    db.delete('ai103:alice:session-1')
elif opts.live and opts.variant=='cosmos':
    from azure.cosmos import CosmosClient
    from azure.identity import DefaultAzureCredential
    client=CosmosClient(env('COSMOS_ENDPOINT'),credential=DefaultAzureCredential())
    db=client.get_database_client(env('COSMOS_DATABASE','ai103')).get_container_client(env('COSMOS_CONTAINER','memory'))
    db.upsert_item({'id':'preference-1','userId':'alice','language':'en','ttl':3600})
    item=db.read_item('preference-1',partition_key='alice')
    result={'userId':item['userId'],'language':item['language']}
    db.delete_item('preference-1',partition_key='alice')
elif opts.live:
    raise ValueError('Choose --variant redis or cosmos')
else:
    db=Memory(':memory:')
    db.put('alice','s1',messages)
    result={'alice':db.get('alice','s1'),'bob':db.get('bob','s1'),'window':window(messages,30)}
    db.close()
save('15_memory.json',result)
