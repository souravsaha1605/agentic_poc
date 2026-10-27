# Purpose: Query an operational vector store
# Learn: Inspect Cosmos vector configuration and contrast operational storage with a dedicated search index.
# Run: Import databricks/extensions/30_cosmos_vector.py as a Databricks source notebook. Start live=false; read labs/30_enterprise_grounding_and_operational_data/RUNBOOK.md.

"""Optional real Cosmos query using illustrative 3D vectors, NOT semantic embeddings."""
from academy.common import args,env,save
opts=args('Create a learning vector container and query it')
if not opts.live:
    save('30_cosmos_vector.json', {'mode': 'contract preview; no Cosmos call', 'next': 'Create vector container through Portal, then live=true'})
else:
    from azure.cosmos import CosmosClient,PartitionKey
    from azure.identity import DefaultAzureCredential
    client=CosmosClient(env('COSMOS_ENDPOINT'),credential=DefaultAzureCredential())
    db=client.get_database_client(env('COSMOS_DATABASE','ai103'))
    container=db.get_container_client('ai103-vectors')
    for item in [{'id':'a','tenant':'retail','text':'return policy','vector':[1.,0.,0.]},
                 {'id':'b','tenant':'retail','text':'shipping','vector':[0.,1.,0.]}]:container.upsert_item(item)
    rows=list(container.query_items(query='SELECT TOP 2 c.id, c.text, VectorDistance(c.vector, @v) AS distance FROM c ORDER BY VectorDistance(c.vector, @v)',
        parameters=[{'name':'@v','value':[1.,0.,0.]}],partition_key='retail'))
    save('30_cosmos_vector.json',{'rows':rows,'container_retained':'ai103-vectors; delete in portal after inspection'})
