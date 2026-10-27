# Redis Cosmos DB Fabric and OneLake

## Redis session state

Create an approved Redis-compatible Azure cache in the portal and choose a small learning
configuration. Use TLS and the authentication method supported by that resource. For this
introductory redis-py example, store a TLS URL such as `rediss://:<credential>@<host>:<port>/0`
in REDIS_URL through the secret scope. Do not print it. Service offerings and authentication
options change; select the supported offering in your subscription rather than assuming an
old cache SKU is still offered. Production Entra authentication requires the appropriate
supported client credential integration, not simply replacing a password with a static token.

Run lab 15 with variant=redis. It writes a synthetic session with a 60-second TTL, reads it,
then removes it. Test TTL expiry and another user's key. Keys include user/session identifiers;
this naming convention is not itself access control. Enforce access before looking up the key.

## Cosmos DB durable state

Azure Portal → Azure Cosmos DB → create an account for NoSQL in your learning group.
In Data Explorer create database `ai103` and container `memory`, partition key `/userId`.
Enable TTL with a default of -1 if you want individual items to choose their expiry.
The lab writes a synthetic preference with ttl=3600 and deletes it after reading.

Use Entra ID for the Python client. Assign the notebook/service principal a Cosmos DB
**data-plane** role; Azure management-plane Contributor is insufficient. An administrator can
use Azure Cloud Shell to assign the built-in data contributor role, scoped appropriately:

```bash
az cosmosdb sql role assignment create --resource-group <learning-rg> --account-name <account> --role-definition-id 00000000-0000-0000-0000-000000000002 --principal-id <principal-object-id> --scope /dbs/ai103
```

Set COSMOS_ENDPOINT and the identity credentials described in DATABRICKS.md. Run lab 15 with
variant=cosmos. A 403 can mean the wrong plane/scope, not a bad endpoint. For production separate
read/write roles and app authorization. A partition key does not prevent a privileged client
from querying another user's partition.

For the advanced vector extension in lab 30, enable vector search for the account where
required, create a separate container `ai103-vectors` with partition key `/tenant` in Data Explorer.
Configure its vector embedding/index policies from lab 30's `vector_policy.json` (the file describes
portal settings; it is not itself an ARM template). Then run `cosmos_vector.py --live`. It uses a flat
index with deliberately short illustrative vectors so you can inspect the math. These are not
real semantic embeddings. Extend it using lab 08's model embeddings and a suitable index type;
check dimension/feature constraints and recreate immutable vector policy structures as needed.

## Fabric and OneLake

This is a handbook extension; it requires Fabric capacity/trial and appropriate workspace
permissions in addition to Azure resources. In Fabric create a learning workspace and Lakehouse.
Upload `data/enterprise/sales.csv` into Files, load it as table `ai103_sales`, and open the SQL
analytics endpoint. Copy its connection details; use an approved Entra authentication method.
For a Python ODBC experiment install ODBC Driver 18 and pyodbc on supported compute and store
FABRIC_SQL_CONNECTION_STRING securely. In Databricks, use a permitted native-driver setup or
run the query in Fabric's portal when the cluster lacks ODBC. Do not use a SQL password invented
for an Entra-only endpoint.

Run lab 30 with variant=fabric. It issues a parameterized read of the synthetic IN rows. Test
with a restricted identity and enforce the table/view row/column rules appropriate to the
SQL engine and access path. A shortcut in OneLake does not automatically make all source data
safe for all agents. Combine this analytical result with live inventory using separate source
names and timestamps; do not misrepresent a historical aggregate as current stock.

References:
- https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/how-to-connect-role-based-access-control
- https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/how-to-python-vector-index-query
- https://learn.microsoft.com/en-us/fabric/data-warehouse/entra-id-authentication
