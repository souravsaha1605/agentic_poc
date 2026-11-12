# Azure deployment learning session: setup you can do now

Prepared for a 5–6 hour session on 12 November 2026 (India time). Check the actual subscription expiration timestamp and its displayed timezone in Azure Portal/Billing; convert it to India time (UTC+05:30). A calendar date does not establish the cutoff hour. This guide is a plan and runnable setup sequence, not evidence that resources have been deployed.

## Recommendation and three industry patterns

| Pattern | Main path | Tradeoff | Use today |
|---|---|---|---|
| Single-tenant web/API workload | Client → authenticated API on App Service → deterministic tools/RAG → Azure services; managed identity, Key Vault, monitoring | Simple identity boundary and broad Azure learning; enterprise deployment still needs real user authentication, access controls, operations and HA | Recommended. Teams is optional. Deploy the forecast RCA web adapter when available; the academy API below is an existing fallback |
| Teams enterprise copilot | Teams → Azure Bot/Agents SDK → queue → worker → Blob state/Databricks SQL; Entra user mapping | Strong employee experience, but custom app upload, Bot registration, admin consent and user licensing can block a personal/student tenant | Only attempt after the web/API succeeds and tenant capability is confirmed |
| Split subscriptions/tenants | Azure backend in the expiring subscription; Teams app registered/installed in the student tenant, or all resources moved to one permitted tenant | Cross-tenant architecture occurs in SaaS, but requires deliberate app audience, issuer validation, consent, resource access and ownership. Student privileges do not automatically grant access to the personal tenant | Do not make this the critical path today. Keep lab accounts separate; export artifacts and recreate in the surviving subscription |

A student Microsoft 365 account may have Teams access but lack custom-app upload or tenant admin consent. A personal Microsoft account can own Azure resources but is not equivalent to a licensed work/school Teams user. Check policies rather than assuming either account has the required rights. Do not copy credentials between accounts or weaken tenant validation.

## First 20 minutes: inspect access and preserve evidence

1. Azure Portal → directory/subscription picker: confirm which subscription has the remaining credit and its directory.
2. Subscription → Overview/Cost Management/Billing: inspect status, expiry/credit details, regional restrictions and available quota. Budget alerts can lag and do not stop spend. Keep everything in a new, dedicated learning resource group.
3. Subscription → Access control (IAM) → View my access: identify your role. Resource creation needs appropriate management rights; assigning managed-identity data roles needs role-assignment permission (Owner, User Access Administrator, RBAC Administrator, or a suitable custom role). Contributor alone generally cannot assign roles.
4. Open Azure Cloud Shell Bash. Run these read-only checks:

```bash
az account list --query '[].{name:name,id:id,tenant:tenantId,state:state}' -o table
az account set --subscription 'YOUR_SUBSCRIPTION_ID'
az account show --query '{name:name,id:id,tenant:tenantId,state:state}' -o table
az provider show --namespace Microsoft.Web --query registrationState -o tsv
az provider show --namespace Microsoft.CognitiveServices --query registrationState -o tsv
az provider show --namespace Microsoft.Search --query registrationState -o tsv
```

5. Before creating resources, confirm a supported region and an agreed spending limit. Check Foundry model deployments/quota early; model access and capacity differ by subscription and region. Do not spend an hour waiting for a restricted model. Use the deterministic API first and substitute an available supported model for the isolated model lab.
6. Keep a local evidence folder on your computer. Save sanitized screenshots, resource IDs, deployment IDs, request IDs, successful/failed results, architecture and cleanup commands. Export these **before** the subscription expires. Do not export keys, tokens, connection strings, Cloud Shell credential files or private user data.

## Hour 0–1.5: deploy the forecast RCA API without Teams

The chosen main application is forecast RCA with the new web learning adapter. This avoids Teams tenant requirements. It runs certified synthetic data with durable Azure Blob state, managed-identity authentication and optimistic concurrency across two Gunicorn workers on one app instance. This is an industry-style layered learning deployment, not an HA production release. The existing full Bot/Teams template is a separate path; do not deploy it for this web exercise.

In Azure Cloud Shell Bash, obtain this repository through its normal authorized GitHub route. If private Git access is unavailable, upload the reviewed source archive rather than putting a GitHub token in a URL. Start in `agentic_poc/forecast-intelligence-rca-agent-2` and inspect the new template's actual parameters before running create:

```bash
cd agentic_poc/forecast-intelligence-rca-agent-2
export LEARNING_RG=rg-forecast-learning
export LEARNING_REGION=YOUR_APPROVED_REGION
az group create --name "$LEARNING_RG" --location "$LEARNING_REGION"
# Create the Entra registration/role below first; replace these non-secret IDs/names.
export FORECAST_APP=YOUR_GLOBALLY_UNIQUE_APP_NAME
export FORECAST_STORAGE=YOUR_UNIQUE_LOWERCASE_STORAGE_NAME
export FORECAST_TENANT=YOUR_ENTRA_TENANT_ID
export FORECAST_CLIENT=YOUR_ENTRA_APPLICATION_CLIENT_ID
az deployment group validate --resource-group "$LEARNING_RG" --template-file deployment/learning/azuredeploy.json --parameters appName="$FORECAST_APP" storageName="$FORECAST_STORAGE" location="$LEARNING_REGION" entraTenantId="$FORECAST_TENANT" entraClientId="$FORECAST_CLIENT"
az deployment group what-if --resource-group "$LEARNING_RG" --template-file deployment/learning/azuredeploy.json --parameters appName="$FORECAST_APP" storageName="$FORECAST_STORAGE" location="$LEARNING_REGION" entraTenantId="$FORECAST_TENANT" entraClientId="$FORECAST_CLIENT"
# After inspecting what-if and costs:
az deployment group create --name forecast-web --resource-group "$LEARNING_RG" --template-file deployment/learning/azuredeploy.json --parameters appName="$FORECAST_APP" storageName="$FORECAST_STORAGE" location="$LEARNING_REGION" entraTenantId="$FORECAST_TENANT" entraClientId="$FORECAST_CLIENT"
az deployment group show --name forecast-web --resource-group "$LEARNING_RG" --query properties.outputs -o json
python3 deployment/learning/build_package.py --output /tmp/forecast-learning.zip
```

The package excludes credentials, state and notebooks. Deploy it:

```bash
az webapp deploy --resource-group "$LEARNING_RG" --name "$FORECAST_APP" --src-path /tmp/forecast-learning.zip --type zip
```

The new startup is `python -m gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 120 --access-logfile - deployment.learning.web_api:application`. Dependencies and package contents must match the new web adapter. Do not substitute the Teams host or academy startup. Keep LLM disabled and the synthetic backend explicit.

### Single-tenant Entra identity setup

1. Portal → Microsoft Entra ID → App registrations → New registration. Choose **Accounts in this organizational directory only**. Record Application/client ID and Directory/tenant ID; IDs are not secrets. Use the directory of the deployment unless deliberately designing cross-tenant access.
2. Authentication → add a **Web** redirect URI `https://YOUR_APP_NAME.azurewebsites.net/.auth/login/aad/callback` after the app name is known.
3. App roles → create role value `Forecast.User`, allowed member types Users/Groups and Applications as required by the final API contract. Enterprise applications → your app → Users and groups → assign your own approved work/school user to the role. User/group assignment and group-based access can depend on directory permissions and licensing. If this is blocked, do not pretend role-based access is enabled; use the original local CLI while directory permissions are fixed and record the limitation. This web adapter has no shared-token fallback.
4. If App Service's authorization-code login configuration requires a client secret, create one in the app registration, then put its value only in the Portal's secure App Service environment-variable editor as `MICROSOFT_PROVIDER_AUTHENTICATION_SECRET`. Never paste it into chat, CLI arguments, source or screenshots. Prefer a Key Vault reference when configured. Copy the value securely once; keep expiration short for the lab.
5. Configure the template's `entraTenantId` and `entraClientId` with the recorded IDs. App Service Authentication must require authentication, return 401 for unauthenticated API access and restrict issuer/audience to this tenant/application. Follow the final deployment guide for any additional parameters. Restart after settings are saved.
6. Open `https://YOUR_APP_NAME.azurewebsites.net/.auth/login/aad` in your browser, sign in as the assigned user, and use the authenticated browser session to exercise the API. This avoids assuming Azure CLI already has consent to a new custom API scope. A direct bearer-token client instead requires the exposed API scope/application permissions, consent, correct audience and role claim; do not use an ARM management token against the application.
7. Test unauthenticated request → 401, authorized assigned user → forecast response, and authenticated unassigned user → denied. App Service injects trusted identity headers; the app must reject fake client-provided headers through the public ingress. Do not disable platform authentication while relying on those headers.

Require a forecast response for `Analyze forecast performance for P0001 in North.` with synthetic accuracy 88.89%, a revenue follow-up of INR 12825.0 and context preserved after app restart. Open the authenticated root URL for the browser interface. Its API is POST `/ask` with JSON `{"message":"Analyze forecast performance for P0001 in North.","session_id":"learning","request_id":"UNIQUE_UUID","channel":"development"}`. Reuse the session for follow-ups and use a new request ID per turn; replay an identical request ID only to test deduplication. `/health` is public liveness; authenticated `/ready` initializes the backend but a successful `/ask` must demonstrate real state reads/writes. Save request IDs and sanitized responses. Inspect Deployment Center logs and Log stream on startup failure. Test repeat deployment and restart. The deployed API uses Azure Blob durable state through a user-assigned managed identity and Storage Blob Data Contributor, with shared-key access disabled. The template also creates a B1 plan, Entra platform authentication, Log Analytics and App Service diagnostics. It does not create Key Vault, AI models, Search, Databricks or Application Insights. Data access is synthetic-lab-wide for assigned Forecast.User identities; real enterprise per-user scope grants, HA, private connectivity and tested recovery remain production work.

The academy API remains a separate optional lab with its original `infra/main.bicep`, authenticated `/ask` and `/skill`, and synthetic local policy retrieval. Deploy it only if time remains and avoid an accidental second paid App Service plan.

## Hour 1.5–3: add RAG and managed identity

Prioritize one small model deployment, Blob and Search, rather than provisioning every service simultaneously.

1. Create a Foundry/Azure AI resource supported by the subscription and region. Deploy one available inexpensive chat model and one embedding model if quota permits. Use small input and output limits; verify one request and record actual usage. Model names, quotas and API versions must come from the actual resource, not guesses.
2. App identity → grant only the inference data role required by that model/resource. For an Azure OpenAI resource, use the applicable `Cognitive Services OpenAI User` role at resource scope. Granting a role can take time to propagate; a role assignment is not proof the call works.
3. For the optional academy API configure `MODEL_AUTH=entra` and the model settings listed in its setup docs. Configure Content Safety separately before enabling its live route. Keep `API_LIVE=false` until both required service calls succeed. Do not claim the API uses Azure Search: the current route retrieves the synthetic local corpus unless a separate Search integration has been implemented and tested.
4. Create StorageV2 with public blob access disabled. Create a private source container; upload only synthetic course documents.
5. Create one Azure AI Search service in a supported tier/region. Enable its system identity and grant the source-container access required for Blob indexing. Build an index from the two sample documents, run its indexer once, inspect execution history, and query in Search Explorer. Free Search availability and skill capabilities vary; use the lowest supported tier and record its cost.
6. Follow `docs/setup/05_SEARCH_AND_INGESTION.md` and lab 09/11 for lexical, vector and hybrid retrieval. Record source IDs, one correct answer, one missing-evidence answer, and a malicious instruction embedded in a document that must remain data.
7. If using secrets, store them in Key Vault via the Portal's secure editor. Give the app only required secret-read access and configure a Key Vault reference in app settings. Verify an actual service request; never put a key into Git or a notebook output.

## Hour 3–4.5: short service labs aligned to the handbook

Use 10–20 minute, synthetic-input experiments. Finish one successful request, one negative case and evidence capture per chosen service. Deployment/region/approval availability may prevent some services today; record those as unrun, not passed.

| Service/capability | Concrete lab | Repository entry |
|---|---|---|
| Language | Detect language, redact PII, extract entities/key phrases, sentiment; verify PII is absent from logged/model-bound text | labs/06_language_and_pii_preprocessing |
| Translator | Translate one short synthetic request and answer; preserve named entities | labs/07_translation_and_multilingual_flow |
| Document Intelligence | Analyze a synthetic receipt and compare extracted totals/fields with ground truth | labs/25_document_intelligence_receipts_and_layout |
| Vision/multimodal | Caption one permitted product image; compare description to actual visible content | labs/24_vision_accessibility_and_visual_safety |
| Speech | Transcribe a short self-recorded clip and synthesize one sentence; use native fallback only if required | labs/27_speech_transcription_synthesis_translation; azure_execution/native_vm |
| Content Safety | Submit one safe and one known policy-test input; inspect categories/threshold decisions | labs/04_content_safety_input_and_output |
| Cosmos DB | Store a synthetic case using an explicit partition key; verify ownership/read isolation | labs/15_memory_windows_redis_and_cosmos |
| Logic Apps | HTTP trigger → 202 → manual approved/rejected synthetic decision; inspect run history | azure_execution/logic_apps |
| Content Understanding | Analyze one small supported file and validate structured fields | labs/26_content_understanding_analyzers |

Verify the exact directory names with `ls labs` in your checkout before running. The handbook describes concepts, not permission to execute document instructions or evidence of current service availability. Image/video generation and Fabric trials can require different capacity, geography or approval; keep them optional today. Databricks is useful for governed batch/SQL analytical work, but it is not required to call ordinary Azure AI services and can consume precious setup time.

## Hour 4.5–5.5: operations and one end-to-end story

Choose one journey: a synthetic receipt arrives → extraction → PII filtering → retrieval of policy → model-assisted explanation with citations → deterministic eligibility → human approval; no actual payment. Or use forecast RCA: request → authorized deterministic forecast/inventory tools → durable case → optional bounded model explanation.

Capture a request correlation ID across the parts that actually support tracing. Open Log stream and Log Analytics for the forecast deployment; inspect Application Insights only if you separately deployed/instrumented it. Confirm actual log records exist rather than assuming a workspace means telemetry works. Run unauthorized, missing evidence and service-timeout cases. Inspect error handling; do not retry non-idempotent actions blindly. Export ARM/Bicep, source package and sanitized evidence. Explain which controls are deployed, which are simulated and which are production follow-ups.

Teams can be a bonus: in the student tenant check Teams admin/custom app upload policy, permitted Bot identity type and user licensing. The forecast repository's Teams path requires a verified identity map, Bot authentication, durable state/queue and actual release-gate tests. Do not set its acceptance flags merely to get a demo working. Cross-tenant student/personal wiring must be explicitly designed and tested; otherwise retain the working web/API channel.

## Last 30 minutes: cleanup and retain learning artifacts

1. Download source, templates, sanitized outputs and screenshots before credit expiry. Do not assume an expired subscription preserves accessible compute or storage. Expiration/disabled-state behavior varies by offer; Azure Portal/Billing is authoritative.
2. Delete the dedicated lab resource group after reviewing its contents. The command below deletes every resource in that group; substitute only the dedicated group you created:

```bash
az resource list --resource-group "$LEARNING_RG" --query '[].{name:name,type:type}' -o table
az group delete --name "$LEARNING_RG" --yes --no-wait
az group wait --name "$LEARNING_RG" --deleted
```

3. Check for resources created in other groups, Search services, Databricks compute/warehouses, managed online endpoints, standalone disks/IPs and connector connections. Stopping an App Service app does not remove its plan charges. Budgets are alerts, not caps. Do not delete unrelated resources.
4. Keep the reusable deployment package and record how to redeploy into the student/next subscription with new IDs and identity bindings. Subscription expiry is not a migration strategy.

Primary repository references: `forecast-intelligence-rca-agent-2/AZURE_SETUP.md`, `forecast-intelligence-rca-agent-2/deployment/RUN_CLOUD.md`, and `chatgpt_project/AI103/ai103-hands-on-academy_2/azure_execution/README.md`.

## Faster Cloud Shell service exercises

The academy now includes `azure_execution/QUICK_SERVICE_LABS.md` and `scripts/run_service_lab.py`. These run Language, Document Intelligence, Translator and Speech directly from Cloud Shell, without Databricks. See that guide for isolated dependency installation, hidden credential prompts and exact offline/live commands. Default runs are explicitly fixtures. These services are learning side projects, not integrations in the deployed forecast web API.
