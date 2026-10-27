# Execution runbook — 30 enterprise grounding and operational data

Read this before README experiments. No prior agentic-AI experience is assumed.

## Notebook `extensions/30_cosmos_vector.py`

1. Complete [Databricks setup](../../docs/setup/DATABRICKS.md) and bootstrap.
2. Import `databricks/extensions/30_cosmos_vector.py` into Workspace as a Python source notebook and attach compute.
3. Set `project_root` to the printed bootstrap path and `output_root` to your writable volume path.
4. Keep `live=false`, `variant=default`, `config_json={}`, and `input_file` blank for the first run.
5. Run cells in order. Find `run_status.json` and the lesson JSON in the unique folder printed at the end.
6. Complete the service setup below. Select a valid live variant, set `live=true`, run package install for `requirements/memory.txt`, then the Python restart cell, then the final execution cell.

**Allowed variants:** default.

### Values to create in the learning Key Vault

Create each needed key under **Objects → Secrets → Generate/Import**. The secret scope is `ai103-lab`. Store even endpoint/name values there so the notebook configuration is repeatable. Never substitute the variable name as its value.

| Key Vault secret name | Where its value comes from |
|---|---|
| `azure-tenant-id` | Azure Portal → Entra ID → Overview → Tenant ID. |
| `azure-client-id` | Entra ID → App registrations → learning app → Application (client) ID. |
| `azure-client-secret` | Same app → Certificates & secrets → new short-lived secret → copy VALUE, not Secret ID. |
| `cosmos-endpoint` | Cosmos DB for NoSQL account → Overview/Keys → URI; authentication remains Entra. |

### Setup and expected checkpoint

Read [06_MEMORY_AND_ENTERPRISE.md](../../docs/setup/06_MEMORY_AND_ENTERPRISE.md) before live calls.

Local two-source join or a parameterized read from your Fabric SQL analytics endpoint.

## Notebook `labs/30_enterprise_grounding_and_operational_data.py`

1. Complete [Databricks setup](../../docs/setup/DATABRICKS.md) and bootstrap.
2. Import `databricks/labs/30_enterprise_grounding_and_operational_data.py` into Workspace as a Python source notebook and attach compute.
3. Set `project_root` to the printed bootstrap path and `output_root` to your writable volume path.
4. Keep `live=false`, `variant=default`, `config_json={}`, and `input_file` blank for the first run.
5. Run cells in order. Find `run_status.json` and the lesson JSON in the unique folder printed at the end.
6. Complete the service setup below. Select a valid live variant, set `live=true`, run package install for `requirements/fabric.txt`, then the Python restart cell, then the final execution cell.

**Allowed variants:** default, fabric.

Offline: default. Live: fabric after ODBC setup. Cosmos vector has its own extension notebook and requires its dedicated container.

### Follow the code

Parameterize a read-only Fabric query or inspect synthetic source separation. Historical sales are not current inventory. Open `labs/30_enterprise_grounding_and_operational_data/run.py`, then follow its `academy` imports into `src/academy/`.

### Values to create in the learning Key Vault

Create each needed key under **Objects → Secrets → Generate/Import**. The secret scope is `ai103-lab`. Store even endpoint/name values there so the notebook configuration is repeatable. Never substitute the variable name as its value.

| Key Vault secret name | Where its value comes from |
|---|---|
| `fabric-sql-connection-string` | Build privately from the SQL endpoint server/database and approved Entra identity; see azure_execution/fabric. |

### Setup and expected checkpoint

Read [06_MEMORY_AND_ENTERPRISE.md](../../docs/setup/06_MEMORY_AND_ENTERPRISE.md) before live calls.

Local two-source join or a parameterized read from your Fabric SQL analytics endpoint.

## If the run fails

- Missing/unreadable key: create the exact listed secret in the scope's backing vault, then
  verify scope read access. A Key Vault IAM Reader role cannot read secret values.
- HTTP 401: key/identity/endpoint mismatch. HTTP 403: data role, scope, firewall or policy.
- HTTP 404: wrong API family, deployment/index/analyzer name or missing resource.
- HTTP 400: unsupported model feature, wrong media shape/language or invalid request schema.
- HTTP 429: wait for the service limit; reduce work or adjust approved quota. Do not retry writes blindly.
- Import/native-library error: rerun the package cell, restart Python, then final cell. For native
  restrictions use [the Azure fallback folder](../../azure_execution/README.md).
- No output: inspect the printed run folder's run_status.json, not an earlier run's JSON.

Do one successful live run and one expected-denial/failure test before marking Azure verified.
Record versions, result path and cleanup in PROGRESS.csv. Local fixtures do not prove model quality.
