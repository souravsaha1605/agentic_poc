# Execution runbook — 25 document intelligence receipts and layout

Read this before README experiments. No prior agentic-AI experience is assumed.

## Notebook `labs/25_document_intelligence_receipts_and_layout.py`

1. Complete [Databricks setup](../../docs/setup/DATABRICKS.md) and bootstrap.
2. Import `databricks/labs/25_document_intelligence_receipts_and_layout.py` into Workspace as a Python source notebook and attach compute.
3. Set `project_root` to the printed bootstrap path and `output_root` to your writable volume path.
4. Keep `live=false`, `variant=default`, `config_json={}`, and `input_file` blank for the first run.
5. Run cells in order. Find `run_status.json` and the lesson JSON in the unique folder printed at the end.
6. Complete the service setup below. Select a valid live variant, set `live=true`, run package install for `requirements/documents.txt`, then the Python restart cell, then the final execution cell.

**Allowed variants:** default, layout, read, custom.

default=receipt, layout=layout/tables, read=OCR text, custom=your trained model. For custom set config_json {"DOCUMENT_MODEL_ID":"your-model-id"}.

### Follow the code

Submit image bytes → wait for Document Intelligence → retain fields/layout/confidence. Missing extraction is not authorization to act. Open `labs/25_document_intelligence_receipts_and_layout/run.py`, then follow its `academy` imports into `src/academy/`.

### Values to create in the learning Key Vault

Create each needed key under **Objects → Secrets → Generate/Import**. The secret scope is `ai103-lab`. Store even endpoint/name values there so the notebook configuration is repeatable. Never substitute the variable name as its value.

| Key Vault secret name | Where its value comes from |
|---|---|
| `document-endpoint` | Document Intelligence resource → Keys and Endpoint → endpoint. |
| `document-key` | Same Document Intelligence resource → Keys and Endpoint → key. |

### Setup and expected checkpoint

Read [10_DOCUMENTS_AND_MEDIA.md](../../docs/setup/10_DOCUMENTS_AND_MEDIA.md) before live calls.

Extracted receipt fields or page/table structure. Offline fields are explicitly synthetic fixtures.

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
