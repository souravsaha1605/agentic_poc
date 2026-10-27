# Execution runbook — agentic analyzer

Read this before README experiments. No prior agentic-AI experience is assumed.

## Notebook `extensions/26_agentic_analyzer.py`

1. Complete [Databricks setup](../../docs/setup/DATABRICKS.md) and bootstrap.
2. Import `databricks/extensions/26_agentic_analyzer.py` into Workspace as a Python source notebook and attach compute.
3. Set `project_root` to the printed bootstrap path and `output_root` to your writable volume path.
4. Keep `live=false`, `variant=default`, `config_json={}`, and `input_file` blank for the first run.
5. Run cells in order. Find `run_status.json` and the lesson JSON in the unique folder printed at the end.
6. Complete the service setup below. Select a valid live variant, set `live=true`, run package install for `requirements/core.txt`, then the Python restart cell, then the final execution cell.

**Allowed variants:** default, create.

### Values to create in the learning Key Vault

Create each needed key under **Objects → Secrets → Generate/Import**. The secret scope is `ai103-lab`. Store even endpoint/name values there so the notebook configuration is repeatable. Never substitute the variable name as its value.

| Key Vault secret name | Where its value comes from |
|---|---|
| `cu-endpoint` | Foundry resource used by Content Understanding Studio → Keys and Endpoint → root endpoint. |
| `cu-key` | Same resource key; model defaults/mappings must already work in CU Studio. |

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

## Exact exercise

Complete GA lab 26 first and read azure_execution/content_understanding/README.md.
In CU Studio configure the current supported completion-model mapping and adequate quota.
Set config_json={"CU_API_VERSION":"2026-06-01-preview","CU_ANALYZER":"ai103-receipt-review","CU_COMPLETION_MODEL":"gpt-5.2"}
only if gpt-5.2 is a currently supported mapped model in your resource; otherwise use the supported
model family name from its settings. Run live=true variant=create once, then variant=default.
Create retains the analyzer; default analyzes receipt.png. Inspect ArithmeticReview against the
receipt. If quota/preview access is unavailable, record blocked; the historical pro API is retired.
