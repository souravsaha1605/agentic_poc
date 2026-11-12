# Short service labs from Azure Cloud Shell

No Databricks workspace is required for these Python entry points. Use only synthetic supplied inputs. Each service still needs its own allowed subscription, region, provisioned resource, endpoint and credentials. Source runbooks retain their Databricks route; this is a quicker alternate execution host.

From the academy root, create an isolated virtual environment. Keep it separate from forecast RCA, because the projects have different model SDK constraints:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
# These default runs use fixtures and make zero Azure calls:
python scripts/run_service_lab.py language
python scripts/run_service_lab.py documents
python scripts/run_service_lab.py translator
python scripts/run_service_lab.py speech
```

For live calls, create the corresponding resource in Portal and open Keys and Endpoint. Complete the service setup guides before proceeding. Keys are read with a hidden terminal prompt, never stored by this launcher. Existing environment bindings are reused without printing values. Use a private interactive terminal. Do not screenshot prompt entries or dump your environment.

| Lab | Provision and learn | Install | Live command | Expected checkpoint |
|---|---|---|---|---|
| Language | Azure AI Language: PII, entities, sentiment | `python -m pip install -r requirements/language.txt` | `python scripts/run_service_lab.py language --live` | Service-derived analysis of synthetic Alex Example message |
| Document extraction | Document Intelligence: receipt model and confidence | `python -m pip install -r requirements/documents.txt` | `python scripts/run_service_lab.py documents --live` | Actual fields from bundled synthetic receipt.png |
| Translation | Translator resource, endpoint and region | Base install above | `python scripts/run_service_lab.py translator --live` | English → Hindi → English actual service responses |
| Speech | Speech resource, matching region, native runtime support | `python -m pip install -r requirements/speech.txt` | `python scripts/run_service_lab.py speech --live` | Synthesize then transcribe synthetic sentence; saves audio |

Outputs go to `service-lab-evidence/SERVICE`, or an explicitly set ACADEMY_OUTPUT_DIR. Repeated runs replace that service's JSON checkpoint: copy sanitized results to a dated folder if retaining comparisons. A fixture result is never a live success. A nonzero exit stops the workflow; inspect the missing prerequisite instead of relabeling it as passed. Speech native libraries may require a supported Linux host; use the existing native_vm guide only if Cloud Shell actually fails.

For RAG/model deployment and Azure AI Search use docs/setup/02_FOUNDRY_AND_MODELS.md and 05_SEARCH_AND_INGESTION.md, then labs 09 and 11. For Content Safety use setup/03_SAFETY.md and lab 04; its live mode performs both safety and model requests and needs both configured. Keep these isolated from the deployed forecast app: the new forecast web adapter deliberately makes no model calls and does not claim these labs are integrated.

Prioritize model/Search, Language and Document Intelligence after the main deployment works. Translator/Speech, Cosmos DB and Logic Apps follow if time and quotas permit. Content Understanding, image/video generation, Fabric and Teams are optional extensions. Record successful requests and one meaningful error/denial per service you actually test; do not claim complete course or production coverage from one short exercise.
