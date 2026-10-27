# Execution runbook — 16 foundry managed agent

Read this before README experiments. No prior agentic-AI experience is assumed.

## Notebook `labs/16_foundry_managed_agent.py`

1. Complete [Databricks setup](../../docs/setup/DATABRICKS.md) and bootstrap.
2. Import `databricks/labs/16_foundry_managed_agent.py` into Workspace as a Python source notebook and attach compute.
3. Set `project_root` to the printed bootstrap path and `output_root` to your writable volume path.
4. Keep `live=false`, `variant=default`, `config_json={}`, and `input_file` blank for the first run.
5. Run cells in order. Find `run_status.json` and the lesson JSON in the unique folder printed at the end.
6. Complete the service setup below. Select a valid live variant, set `live=true`, run package install for `requirements/agents.txt`, then the Python restart cell, then the final execution cell.

**Allowed variants:** default.

### Follow the code

Create agent version in Foundry → create conversation → send two turns → remove conversation. Keep agent version for portal inspection. Open `labs/16_foundry_managed_agent/run.py`, then follow its `academy` imports into `src/academy/`.

### Values to create in the learning Key Vault

Create each needed key under **Objects → Secrets → Generate/Import**. The secret scope is `ai103-lab`. Store even endpoint/name values there so the notebook configuration is repeatable. Never substitute the variable name as its value.

| Key Vault secret name | Where its value comes from |
|---|---|
| `azure-tenant-id` | Azure Portal → Entra ID → Overview → Tenant ID. |
| `azure-client-id` | Entra ID → App registrations → learning app → Application (client) ID. |
| `azure-client-secret` | Same app → Certificates & secrets → new short-lived secret → copy VALUE, not Secret ID. |
| `foundry-project-endpoint` | Foundry project overview → project endpoint ending /api/projects/PROJECT; not inference root. |
| `model-small` | Foundry → Models/Deployments → your chat deployment NAME; supports structured output and tools. |

### Setup and expected checkpoint

Read [02_FOUNDRY_AND_MODELS.md](../../docs/setup/02_FOUNDRY_AND_MODELS.md) before live calls.

The second response recalls K100. The agent version remains for portal inspection; the sample conversation is deleted.

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
