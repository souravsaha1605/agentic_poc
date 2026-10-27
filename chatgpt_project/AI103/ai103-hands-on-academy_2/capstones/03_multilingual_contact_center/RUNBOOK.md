# Execution runbook — 03 multilingual contact center

Read this before README experiments. No prior agentic-AI experience is assumed.

## Notebook `capstones/03_multilingual_contact_center.py`

1. Complete [Databricks setup](../../docs/setup/DATABRICKS.md) and bootstrap.
2. Import `databricks/capstones/03_multilingual_contact_center.py` into Workspace as a Python source notebook and attach compute.
3. Set `project_root` to the printed bootstrap path and `output_root` to your writable volume path.
4. Keep `live=false`, `variant=default`, `config_json={}`, and `input_file` blank for the first run.
5. Run cells in order. Find `run_status.json` and the lesson JSON in the unique folder printed at the end.
6. Complete the service setup below. Select a valid live variant, set `live=true`, run package install for `requirements/contact_center.txt`, then the Python restart cell, then the final execution cell.

**Allowed variants:** default, speech.

### Values to create in the learning Key Vault

Create each needed key under **Objects → Secrets → Generate/Import**. The secret scope is `ai103-lab`. Store even endpoint/name values there so the notebook configuration is repeatable. Never substitute the variable name as its value.

| Key Vault secret name | Where its value comes from |
|---|---|
| `azure-openai-endpoint` | Foundry/OpenAI inference resource → Keys and Endpoint → root HTTPS endpoint; no /openai path. |
| `azure-openai-api-key` | Same inference resource → Keys and Endpoint → Key 1 or Key 2. |
| `model-small` | Foundry → Models/Deployments → your chat deployment NAME; supports structured output and tools. |
| `model-embedding` | Your text-embedding deployment NAME, not a chat deployment. |
| `search-endpoint` | Azure AI Search service → Overview → URL (https://...search.windows.net). |
| `search-admin-key` | Search service → Settings → Keys → admin key for the dedicated learning index. |
| `safety-endpoint` | Content Safety resource → Keys and Endpoint → root endpoint. |
| `safety-key` | Same Content Safety resource → Keys and Endpoint → key. |
| `language-endpoint` | Language resource → Keys and Endpoint → root endpoint. |
| `language-key` | Same Language resource → Keys and Endpoint → key. |
| `translator-key` | Translator resource → Keys and Endpoint → key. |
| `translator-region` | Translator resource region/code from Keys and Endpoint, e.g. centralindia where supported. |

Optional keyless model calls: config_json={"MODEL_AUTH":"entra"}; create azure-tenant-id, azure-client-id, azure-client-secret and assign the model data role to that app. Other services in this lesson may still use keys.

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

## Complete speech path (implemented)

First run lab 27 and retain its sample.wav or upload your own short WAV. In this capstone select
variant=speech, live=true, input_file=/Volumes/.../sample.wav. Add speech-key and speech-region to
the scope; use config_json {"SPEECH_LANGUAGE":"en-US"} for the English sample. The notebook installs
requirements/contact_center.txt. The pipeline transcribes, removes PII, translates as needed,
retrieves/answers, checks output and synthesizes reply.wav. Use a supported multilingual voice.
This is single-utterance interaction, not a streaming voice server. The native-VM fallback applies.
