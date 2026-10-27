# Execution runbook — 18 sequential and concurrent workflows

Read this before README experiments. No prior agentic-AI experience is assumed.

## Notebook `labs/18_sequential_and_concurrent_workflows.py`

1. Complete [Databricks setup](../../docs/setup/DATABRICKS.md) and bootstrap.
2. Import `databricks/labs/18_sequential_and_concurrent_workflows.py` into Workspace as a Python source notebook and attach compute.
3. Set `project_root` to the printed bootstrap path and `output_root` to your writable volume path.
4. Keep `live=false`, `variant=default`, `config_json={}`, and `input_file` blank for the first run.
5. Run cells in order. Find `run_status.json` and the lesson JSON in the unique folder printed at the end.
6. Keep `live=false`: this notebook does not have an Azure service-call branch. No service keys or optional SDK installation are needed.

**Allowed variants:** default, failure.

failure demonstrates one failed concurrent branch and one successful branch.

### Follow the code

Measure serial awaits → overlap independent tasks → collect partial failures. This is real Python concurrency but synthetic I/O. Open `labs/18_sequential_and_concurrent_workflows/run.py`, then follow its `academy` imports into `src/academy/`.

### Setup and expected checkpoint

Read [ARCHITECTURE.md](../../docs/ARCHITECTURE.md) before live calls.

Concurrent work usually takes roughly the slower branch time. --variant failure returns one result plus one error.

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
