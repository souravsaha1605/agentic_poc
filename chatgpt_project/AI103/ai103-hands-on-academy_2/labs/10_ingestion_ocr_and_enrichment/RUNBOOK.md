# Execution runbook — 10 ingestion ocr and enrichment

Read this before README experiments. No prior agentic-AI experience is assumed.

## Notebook `labs/10_ingestion_ocr_and_enrichment.py`

1. Complete [Databricks setup](../../docs/setup/DATABRICKS.md) and bootstrap.
2. Import `databricks/labs/10_ingestion_ocr_and_enrichment.py` into Workspace as a Python source notebook and attach compute.
3. Set `project_root` to the printed bootstrap path and `output_root` to your writable volume path.
4. Keep `live=false`, `variant=default`, `config_json={}`, and `input_file` blank for the first run.
5. Run cells in order. Find `run_status.json` and the lesson JSON in the unique folder printed at the end.
6. Keep `live=false`: this notebook does not have an Azure service-call branch. Complete the linked cloud exercise under [azure_execution](../../azure_execution/README.md) separately.

**Allowed variants:** default.

### Follow the code

Hash source files → chunk text → retain source names. Cloud OCR/enrichment runs in the Search indexer, not in this script. Open `labs/10_ingestion_ocr_and_enrichment/run.py`, then follow its `academy` imports into `src/academy/`.

### Setup and expected checkpoint

Read [05_SEARCH_AND_INGESTION.md](../../docs/setup/05_SEARCH_AND_INGESTION.md) before live calls.

Stable source names, content hashes and chunk IDs. Cloud success is an indexer run with visible enriched fields.

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
