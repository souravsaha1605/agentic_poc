# Execution runbook — 19 multi agent orchestration and reflection

Read this before README experiments. No prior agentic-AI experience is assumed.

## Notebook `extensions/19_group_discussion.py`

1. Complete [Databricks setup](../../docs/setup/DATABRICKS.md) and bootstrap.
2. Import `databricks/extensions/19_group_discussion.py` into Workspace as a Python source notebook and attach compute.
3. Set `project_root` to the printed bootstrap path and `output_root` to your writable volume path.
4. Keep `live=false`, `variant=default`, `config_json={}`, and `input_file` blank for the first run.
5. Run cells in order. Find `run_status.json` and the lesson JSON in the unique folder printed at the end.
6. Complete the service setup below. Select a valid live variant, set `live=true`, run package install for `requirements/core.txt`, then the Python restart cell, then the final execution cell.

**Allowed variants:** default.

### Values to create in the learning Key Vault

Create each needed key under **Objects → Secrets → Generate/Import**. The secret scope is `ai103-lab`. Store even endpoint/name values there so the notebook configuration is repeatable. Never substitute the variable name as its value.

| Key Vault secret name | Where its value comes from |
|---|---|
| `azure-openai-endpoint` | Foundry/OpenAI inference resource → Keys and Endpoint → root HTTPS endpoint; no /openai path. |
| `azure-openai-api-key` | Same inference resource → Keys and Endpoint → Key 1 or Key 2. |
| `model-small` | Foundry → Models/Deployments → your chat deployment NAME; supports structured output and tools. |

Optional keyless model calls: config_json={"MODEL_AUTH":"entra"}; create azure-tenant-id, azure-client-id, azure-client-secret and assign the model data role to that app. Other services in this lesson may still use keys.

### Setup and expected checkpoint

Read [02_FOUNDRY_AND_MODELS.md](../../docs/setup/02_FOUNDRY_AND_MODELS.md) before live calls.

Three bounded stages: draft, review, revision. --variant handoff passes an explicit state object to a specialist.

## Notebook `labs/19_multi_agent_orchestration_and_reflection.py`

1. Complete [Databricks setup](../../docs/setup/DATABRICKS.md) and bootstrap.
2. Import `databricks/labs/19_multi_agent_orchestration_and_reflection.py` into Workspace as a Python source notebook and attach compute.
3. Set `project_root` to the printed bootstrap path and `output_root` to your writable volume path.
4. Keep `live=false`, `variant=default`, `config_json={}`, and `input_file` blank for the first run.
5. Run cells in order. Find `run_status.json` and the lesson JSON in the unique folder printed at the end.
6. Complete the service setup below. Select a valid live variant, set `live=true`, run package install for `requirements/core.txt`, then the Python restart cell, then the final execution cell.

**Allowed variants:** default, handoff.

handoff changes ownership explicitly; default uses manager/specialist/reviewer. The separate group-discussion notebook has two fixed rounds.

### Follow the code

Specialist drafts → reviewer checks evidence → writer revises once → stop. Review text is observable output, not hidden chain of thought. Open `labs/19_multi_agent_orchestration_and_reflection/run.py`, then follow its `academy` imports into `src/academy/`.

### Values to create in the learning Key Vault

Create each needed key under **Objects → Secrets → Generate/Import**. The secret scope is `ai103-lab`. Store even endpoint/name values there so the notebook configuration is repeatable. Never substitute the variable name as its value.

| Key Vault secret name | Where its value comes from |
|---|---|
| `azure-openai-endpoint` | Foundry/OpenAI inference resource → Keys and Endpoint → root HTTPS endpoint; no /openai path. |
| `azure-openai-api-key` | Same inference resource → Keys and Endpoint → Key 1 or Key 2. |
| `model-small` | Foundry → Models/Deployments → your chat deployment NAME; supports structured output and tools. |

Optional keyless model calls: config_json={"MODEL_AUTH":"entra"}; create azure-tenant-id, azure-client-id, azure-client-secret and assign the model data role to that app. Other services in this lesson may still use keys.

### Setup and expected checkpoint

Read [02_FOUNDRY_AND_MODELS.md](../../docs/setup/02_FOUNDRY_AND_MODELS.md) before live calls.

Three bounded stages: draft, review, revision. --variant handoff passes an explicit state object to a specialist.

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
