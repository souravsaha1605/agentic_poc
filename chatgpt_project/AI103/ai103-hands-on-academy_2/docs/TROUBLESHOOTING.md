# Diagnose the first failing boundary

| Symptom | Check first | Corrective action |
|---|---|---|
| No module named academy | Current Python session and src path | Re-run final notebook import cell after restart; locally install -e . |
| Missing environment variable | Current lab's secret mapping | Create the exact hyphenated secret name and load the scope; never paste a value in chat |
| Secret scope denied | Scope ACL, backing vault and permission model | Use dedicated scope/vault and ask its administrator to grant the narrow read path |
| DefaultAzureCredential fails | Actual notebook workload identity | Load tenant/client/secret for the learning principal; don't assume Databricks login is SDK auth |
| 401 | Credential, token audience, endpoint family | Reauthenticate or correct the key/token scope; a project endpoint is not an inference endpoint |
| 403 | Data-plane role and network rules | Check principal object ID, scope, propagation, private DNS and permitted network path |
| 404 / DeploymentNotFound | Resource root and deployment NAME | Compare with portal deployment details; never guess model IDs or append duplicate paths |
| 400 schema/parameter | Model support and API version | Use a compatible deployment; inspect supported parameters; don't blindly add temperature |
| 429 | Quota, burst rate, concurrent turns | Honor Retry-After, bound concurrency and inspect capacity; retries do not add quota |
| Search dimension error | Embedding model/index dimensions | Create a new index with matching dimensions and re-embed all content |
| Search empty | Ingestion success, query/filter and freshness | Inspect failed documents and tenant filter; distinguish no evidence from service failure |
| Semantic query fails | Feature/tier/configuration | Verify sem config and semantic ranking enablement before testing that mode |
| Agent import error | Projects 1.x versus 2.x | Use requirements/agents.txt in a clean session; do not mix classic snippets |
| asyncio.run already running | Notebook event loop | Use academy.common.run_async; don't nest asyncio.run directly |
| MCP subprocess cannot import | Driver path and PYTHONPATH | Re-run bootstrap/final cell; use permitted dedicated compute |
| Speech native library failure | OS/runtime dependencies | Use a supported classic driver or local environment; record a blocked native prerequisite |
| SQLite locking on volume | Database location | Use in-memory/driver-local state; Cosmos/Redis for durable cloud state |
| Polling timeout | Existing operation/job ID | Inspect/resume status; do not submit another paid write blindly |
| Live evaluation fails | Judge deployment and SDK/API compatibility | Use a compatible judge; validate input schema and installed SDK before changing thresholds |
| Output disappeared | Driver restart versus volume output | Re-run bootstrap; use ACADEMY_OUTPUT_DIR pointing to a writable volume |

Preserve a sanitized traceback, status code, request/job ID, SDK versions and lab ID. Do not
print entire provider requests/responses if they can include sensitive inputs or signed URLs.
Local fixtures are never a fallback for a failed live call.
