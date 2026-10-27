# Execution runbook — 20 human approvals and logic apps

Read this before README experiments. No prior agentic-AI experience is assumed.

## Notebook `labs/20_human_approvals_and_logic_apps.py`

1. Complete [Databricks setup](../../docs/setup/DATABRICKS.md) and bootstrap.
2. Import `databricks/labs/20_human_approvals_and_logic_apps.py` into Workspace as a Python source notebook and attach compute.
3. Set `project_root` to the printed bootstrap path and `output_root` to your writable volume path.
4. Keep `live=false`, `variant=default`, `config_json={}`, and `input_file` blank for the first run.
5. Run cells in order. Find `run_status.json` and the lesson JSON in the unique folder printed at the end.
6. Keep `live=false`: this notebook does not have an Azure service-call branch. Complete the linked cloud exercise under [azure_execution](../../azure_execution/README.md) separately.

**Allowed variants:** default, reject.

Local lab: default approves via a fixed synthetic supervisor; reject denies. Real cloud approval is the separate 20_logic_app_submit extension.

### Follow the code

Pending state blocks execution → supervisor decides → execute only if approved. Cloud connector steps are separate. Open `labs/20_human_approvals_and_logic_apps/run.py`, then follow its `academy` imports into `src/academy/`.

### Setup and expected checkpoint

Read [07_APPROVALS_LOGIC_APPS.md](../../docs/setup/07_APPROVALS_LOGIC_APPS.md) before live calls.

Pending → approved → executed, or pending → rejected. No external transaction occurs.

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
