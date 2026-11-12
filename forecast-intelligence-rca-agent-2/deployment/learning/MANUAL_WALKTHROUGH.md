# Deploy and explain your forecast application in Azure

> **Live status:** follow [DEPLOYMENT_JOURNAL.md](DEPLOYMENT_JOURNAL.md) for what actually happened. Instructions below are a manual procedure, not a claim of successful deployment.
>
> **Chosen subscription:** Azure subscription 1 — `ba631193-a731-4715-8718-5d0dc3b5917c`.
> **Goal:** one authenticated forecast application, durable case state and logs; then selected AI-service labs. Keep Teams outside the first deployment.

## 1. Understand the components before creating anything

| Component | What you learn | Why this application needs it |
|---|---|---|
| Resource group | Deployment boundary and lifecycle | Keeps this exercise identifiable and removable |
| App Service B1 Linux | Hosted Python API, startup and deployment | Runs the forecast browser/API application |
| Entra application | End-user authentication and app roles | Identifies permitted users before forecast execution |
| User-assigned managed identity | Workload identity | Lets the app access Blob without an account key |
| Blob Storage | Persistent state, optimistic concurrency | Preserves owned investigations and deduplicated requests |
| Blob data role | Management-plane versus data-plane authorization | Grants the app the data access it needs |
| Log Analytics + diagnostics | Operational evidence | Receives App Service logs after actual delivery is verified |
| Separate AI-service labs | Breadth without unnecessary app dependencies | Exercises model/Search, extraction, language, speech and safety |

Your user signs in to Entra; the application uses its managed identity for storage. These are different identities. The current deployment uses synthetic facts, not your actual enterprise forecast data. It does not need Databricks or Teams to work.

## 2. Check your subscription and deadline — 5 minutes

1. Sign in to Azure Portal using the account that owns the remaining credit.
2. Use the directory/subscription selector. Open **Subscriptions → Azure subscription 1**.
3. Confirm the ID matches the one above. Record status, offer type, remaining credit and the exact expiry timestamp/timezone. Convert the timestamp to India time (UTC+05:30).
4. Open **Access control (IAM) → View my access**. Record whether you can create resources and assign roles. Contributor does not by itself permit role assignments.
5. Open **Usage + quotas** and inspect available App Service capacity/regions. Free/trial/student offers may restrict SKUs and regions. Do not assume credit means quota.
6. Open Cost Management to inspect spending. A budget is an alert, not a hard stop. Do not upgrade to a paid subscription just to complete this exercise without separately choosing to do so.

**Checkpoint:** correct subscription, non-expired status, a permitted region and appropriate permissions. If these fail, fix the specific prerequisite before deployment.

## 3. Choose your execution host — 5 minutes

### Option A: let Codex execute

The current Codex machine must have Azure endpoint network access plus an authenticated Azure identity. The subscription ID is a resource identifier, not a credential.

- Environment settings: review/save the pending network additions for management.azure.com, login.microsoftonline.com and graph.microsoft.com; publish when the product requests it.
- Additional exact application/SCM/Blob hosts may be needed once names are selected. These are not automatically covered by the three management/authentication domains.
- Authentication: use a supported secure Azure identity connection if available. Alternatively, an Azure CLI sign-in can be started here after network access is working; you complete the Microsoft sign-in yourself. Do not paste passwords, access tokens or client secrets into chat.
- Nothing is deployed by saving an environment network draft.

### Option B: Azure Cloud Shell Bash — fastest manual route

1. Open Azure Portal → Cloud Shell icon → **Bash**.
2. Choose the authorized subscription if prompted. If persistent storage setup is blocked, use a supported temporary Cloud Shell session if offered; download evidence before closing it.
3. Run:

```bash
az account list --query '[].{name:name,id:id,tenant:tenantId,state:state}' -o table
az account set --subscription ba631193-a731-4715-8718-5d0dc3b5917c
az account show --query '{name:name,id:id,tenant:tenantId,state:state}' -o table
```

**Checkpoint:** the output shows the selected subscription and an enabled state. Do not run commands against a different default subscription.

### Recover after a Cloud Shell disconnect

A new Cloud Shell session may reopen in a different or non-persistent home filesystem. Shell variables also disappear. A missing clone does not affect GitHub or Azure resources; it only means the session cannot find its local working copy.

First inspect the current directory and search the home filesystem:

```bash
pwd
find "$HOME" -maxdepth 4 -type d -name 'agentic_poc-azure-learning' 2>/dev/null
```

If the command prints a directory, `cd` to that exact path. If it prints nothing, clone the published feature branch again:

```bash
cd "$HOME"
git clone --branch feat/forecast-azure-learning --single-branch https://github.com/souravsaha1605/agentic_poc.git agentic_poc-azure-learning
cd "$HOME/agentic_poc-azure-learning/forecast-intelligence-rca-agent-2"
git rev-parse --short HEAD
```

Then re-export all deployment variables before subsequent Azure commands. Re-cloning is safe because the source of truth is the remote branch. Do not clone over an existing directory or assume environment variables survived the disconnect.

### Where code resides in a production workflow

Cloud Shell is an administrative workstation, not the production runtime or the canonical source store. Re-cloning after a disconnect is needed only when that workstation has no persistent Cloud Drive or opens with a fresh filesystem.

The expected lifecycle is:

```text
GitHub repository and reviewed commit
    -> CI validates/tests once
    -> CI creates an immutable ZIP or container artifact
    -> artifact is stored with a version/digest
    -> deployment identity releases that exact artifact to App Service
    -> App Service runs its deployed copy; Blob Storage holds runtime state
```

For this manual learning deployment, Cloud Shell temporarily performs the packaging and deployment steps that CI would normally perform. The canonical code remains on the GitHub feature branch. The package builder creates `/tmp/forecast-learning.zip`, and `az webapp deploy` transfers it to App Service. App Service extracts or mounts the deployed content under its managed application filesystem (commonly `/home/site/wwwroot` for Linux App Service); developers should not edit that runtime copy manually. Durable investigations live in Blob Storage and therefore do not belong inside the source checkout or deployment package.

For a mature production pipeline, GitHub Actions should authenticate to Azure with workload identity federation/OIDC, build a versioned artifact from an approved commit, run tests and security checks, deploy the same artifact across environments, and retain release metadata for rollback. A containerized variant would store the immutable image in Azure Container Registry and configure App Service or Container Apps to run a pinned image digest.

## 4. Obtain the reviewed source through Git — 5 minutes

Use the feature branch in your authenticated Azure Cloud Shell session:

```bash
git clone --branch feat/forecast-azure-learning --single-branch https://github.com/souravsaha1605/agentic_poc.git agentic_poc-azure-learning
cd agentic_poc-azure-learning/forecast-intelligence-rca-agent-2
git rev-parse HEAD
ls deployment/learning
```

Record the SHA as the deployed source version. If this destination already exists, inspect it before choosing a new clone location; do not overwrite local work. Private GitHub access needs separate approved GitHub authentication, even though Azure Cloud Shell is authenticated to Azure. Never put tokens into a clone URL.

Verify azuredeploy.json, web_api.py, index.html and build_package.py exist under deployment/learning. Do not deploy the older deployment/azuredeploy.json: it creates the separate Bot/Teams path. If Git access is unavailable, the source archive remains a fallback; extracting it is not itself a deployment.

**Checkpoint:** exact feature-branch source and recorded commit SHA. No GitHub Actions pipeline runs automatically in this branch; CI/CD with Azure OIDC can be added after the manual deployment is verified.

## 5. Choose names and region — 5 minutes

```bash
export LEARNING_SUBSCRIPTION='ba631193-a731-4715-8718-5d0dc3b5917c'
export LEARNING_RG='rg-forecast-learning'
export LEARNING_REGION='REPLACE_WITH_APPROVED_REGION'
export FORECAST_APP='REPLACE_WITH_GLOBALLY_UNIQUE_APP_NAME'
export FORECAST_STORAGE='REPLACE_WITH_UNIQUE_STORAGE_NAME'
az account list-locations --query '[].{name:name,display:displayName}' -o table
az provider show --namespace Microsoft.Web --query registrationState -o tsv
az provider show --namespace Microsoft.Storage --query registrationState -o tsv
az provider show --namespace Microsoft.ManagedIdentity --query registrationState -o tsv
az provider show --namespace Microsoft.OperationalInsights --query registrationState -o tsv
```

Storage names use 3–24 lowercase letters/digits. App names must meet App Service naming rules and be globally unique. A listed Azure region does not guarantee your subscription can provision B1 there; deployment validation and quota evidence are needed.

### Values selected in this learning deployment

- Region candidate: `centralindia`, after B1 Linux appeared in the subscription's App Service location listing.
- App Service name: `forecast-rca-922ccd`; Azure reported `nameAvailable: true`.
- Storage account name: `forecastrca922ccd`; Azure reported `nameAvailable: true`.
- Required Web callback: `https://forecast-rca-922ccd.azurewebsites.net/.auth/login/aad/callback`.

Name checks are read-only and do not reserve names. Configure the callback with the exact app hostname, then let ARM validation and deployment confirm current availability, policy and quota.

If a required provider is not registered and your permissions allow registration, register only that provider with `az provider register --namespace PROVIDER_NAME --wait`. This is a subscription-level change; do not register unrelated services.

## 6. Create your Entra application — 10–20 minutes

1. Portal → **Microsoft Entra ID → Overview**. Confirm the directory associated with the selected subscription.
2. **App registrations → New registration**. Name: `Forecast RCA learning`. Supported account types: **Accounts in this organizational directory only**.
3. Register. Copy **Application (client) ID** and **Directory (tenant) ID**; these are not secrets.
4. **Authentication → Add a platform → Web**. Add `https://YOUR_APP_NAME.azurewebsites.net/.auth/login/aad/callback`, substituting the exact FORECAST_APP. Do not use a SPA redirect for the server-side sign-in route.
5. **App roles → Create app role**. Display name: `Forecast user`; value: `Forecast.User`; description: synthetic forecast investigation access. Enable the role. Choose Users/Groups for browser users; add Applications only if deliberately testing service-to-service access.
6. **Enterprise applications → your application → Users and groups → Add user/group**. Assign your approved user to `Forecast.User`. Individual user assignment and group assignment have different licensing/admin requirements. If blocked, inspect the tenant policy; do not remove authorization checks.
7. **App registrations → your app → Certificates & secrets → New client secret**. Choose a short suitable lifetime. Copy the **value**, not the secret ID, directly to your private password manager until entered securely in App Service. Never paste it into chat, Git, a command argument, a notebook or screenshots.
8. Set non-secret IDs in Cloud Shell:

```bash
export FORECAST_TENANT='YOUR_DIRECTORY_TENANT_ID'
export FORECAST_CLIENT='YOUR_APPLICATION_CLIENT_ID'
```

Do not request Microsoft Graph application permissions just to authenticate users. The minimal app does not read Graph at runtime. The management operator may use Graph while configuring the registration.

**Checkpoint:** correct tenant/client ID, exact callback URL, role exists and user is assigned. Creating an Azure subscription does not grant tenant admin or Teams permissions.

### Result recorded in this learning deployment

- App registration: `Forecast RCA learning`, single tenant.
- Application/client ID: `922ccd1b-86d7-4e0a-87e8-9e1b97bdadc9`.
- Directory/tenant ID: `a71e922d-d0ad-4933-b2a7-201574b5c151`.
- App role value: `Forecast.User`, allowed member type Users/Groups.
- Individual user assignment: succeeded.
- Group assignment: unavailable under the current Entra plan. This does not block the individual learning deployment and does not require a plan upgrade.

Why this sequence matters: the registration identifies the application, single-tenant selection fixes the trusted issuer, the app role expresses authorization, and the enterprise-application assignment grants that role to a user. The deployed adapter validates the tenant, object identity and role claim rather than treating any authenticated account as authorized.

### Why user identity and managed identity are separate

The signed-in user and the deployed workload have different jobs and therefore receive different permissions:

```text
User identity -> signs in and receives Forecast.User -> may use the application
App Service managed identity -> receives scoped Blob data access -> may persist application state
```

This removes Storage account keys from source and deployment packages. Azure issues short-lived tokens to the workload and manages their rotation. Removing a user's Forecast.User assignment blocks that person without interrupting storage access for everyone else. Removing the workload's Blob role retires its data access without changing user accounts. If either identity is compromised, it does not automatically receive the permissions of the other identity or the operator who deployed the resources.

In practice, an assigned analyst can open an owned investigation while another authenticated but unassigned employee receives 403. Neither person receives direct Blob credentials. The application uses its managed identity to reach the private state container and still enforces tenant-and-user ownership before returning a case. Azure activity and data-plane logs can distinguish actions performed by the deploying operator, the application workload and the end user.

## 7. Validate and review infrastructure — 5–15 minutes

Create only the dedicated learning group:

```bash
az group create --name "$LEARNING_RG" --location "$LEARNING_REGION"
az deployment group validate --resource-group "$LEARNING_RG" --template-file deployment/learning/azuredeploy.json --parameters appName="$FORECAST_APP" storageName="$FORECAST_STORAGE" location="$LEARNING_REGION" entraTenantId="$FORECAST_TENANT" entraClientId="$FORECAST_CLIENT"
az deployment group what-if --resource-group "$LEARNING_RG" --template-file deployment/learning/azuredeploy.json --parameters appName="$FORECAST_APP" storageName="$FORECAST_STORAGE" location="$LEARNING_REGION" entraTenantId="$FORECAST_TENANT" entraClientId="$FORECAST_CLIENT"
```

Review every Create/Modify/Delete result. Expected: B1 plan, app, identity, dedicated storage/container, Blob data role, authentication configuration, logs and diagnostics. Unexpected deletions are a reason to stop and investigate. Local JSON parsing cannot replace Azure validation. What-if is also not a guarantee of successful provisioning or data-plane access.

## 8. Deploy resources and package — 10–25 minutes

After validation/what-if and pricing review:

```bash
az deployment group create --name forecast-web --resource-group "$LEARNING_RG" --template-file deployment/learning/azuredeploy.json --parameters appName="$FORECAST_APP" storageName="$FORECAST_STORAGE" location="$LEARNING_REGION" entraTenantId="$FORECAST_TENANT" entraClientId="$FORECAST_CLIENT"
az deployment group show --name forecast-web --resource-group "$LEARNING_RG" --query '{state:properties.provisioningState,outputs:properties.outputs}' -o json
python3 deployment/learning/build_package.py --output /tmp/forecast-learning.zip
az webapp deploy --resource-group "$LEARNING_RG" --name "$FORECAST_APP" --src-path /tmp/forecast-learning.zip --type zip
```

Azure's deployment build installs the package requirements. The package contains source and HTML, not local state or secrets. If a deployment partially fails, inspect actual resources and deployment operations before retrying. Resource creation alone does not prove the Python application started.

### What-if result recorded for this deployment

Azure predicted 11 creates and no modifications or deletions. The expected B1 plan, web app, identity, private keyless Storage account/state container, Blob data role, required single-tenant authentication, Log Analytics workspace and diagnostics were present. No Teams/Bot, model, Databricks, Search, Key Vault, Cosmos or queue resources were predicted. This is the approval boundary before billable infrastructure creation; the B1 plan starts charging once created.

## 9. Finish secure sign-in settings — 5–10 minutes

1. Portal → **App Services → your app → Environment variables/App settings**.
2. Add `MICROSOFT_PROVIDER_AUTHENTICATION_SECRET` with the secret **value** from the Entra app. Save securely. For a separate Key Vault learning exercise you may later replace this with a correctly configured Key Vault reference; the minimal template does not create a vault.
3. Confirm non-secret settings: `FORECAST_WEB_TENANT_ID` matches Entra; `FORECAST_WEB_STATE_BACKEND=azure`; `ENABLE_LLM=false`; the Blob account/container match the deployment.
4. **Authentication**: Microsoft/Entra provider enabled, correct single-tenant issuer/client ID, authentication required, unauthenticated API requests return 401. Only /health is excluded.
5. **Configuration/General settings → Startup command** should match the template's Gunicorn module. Do not substitute the older Teams host.
6. **Identity → User assigned**: confirm the deployment identity is attached. On the storage account **Access control** verify that identity's Blob data role exists. Never enable shared storage keys to work around RBAC.

**Checkpoint:** sign-in secret configured, authorization retained, managed identity attached. A role-assignment entry is not evidence that propagation and actual access are working.

## 10. Prove the complete journey — 15–25 minutes

1. Open `https://APP.azurewebsites.net/health`. Expect `status=alive`. This is not a storage readiness check.
2. Open `/` in an unsigned-in private browser. Expect platform 401.
3. Open `https://APP.azurewebsites.net/.auth/login/aad`, sign in with your assigned user, then return to `/`.
4. Ask `Analyze forecast performance for P0001 in North.` Expect synthetic accuracy **88.89%**.
5. Ask `What about revenue?` Expect net revenue **INR 12825.0** in the same investigation.
6. Ask `What if demand is 15% higher?` Expect the arithmetic scenario **1552.5 units** from **1350**. This is not an enterprise prediction.
7. Restart the app, use the same browser session, and verify follow-up context survives. This exercises Blob persistence across process lifetime.
8. Use an unassigned identity: expect denial. Do not grant extra roles merely to avoid testing the denial.
9. Repeat the exact same POST body with the same request_id in an authenticated API client: it must replay without another scenario version. The UI generates a new ID on each submission, so repeated clicks are not this test.
10. Open **Log stream** and your Log Analytics workspace. Verify actual entries, statuses, timestamps and correlation IDs. Authentication failures handled by the platform may not reach application logging.

Record the outcome and sanitized evidence for each check. Do not capture tokens, cookies, principal headers or secret app settings.

## 11. Learn additional services — next 2–3 hours

Open the sibling academy's `azure_execution/QUICK_SERVICE_LABS.md` for Cloud Shell runs. First use the explicitly offline mode, then configure one resource and run --live. Model/Search, Document Intelligence and Language are the highest-priority additions. Follow with Speech/Translator and Content Safety, then Cosmos DB/Logic Apps if time remains. Use the existing setup guides for provisioning and service-specific permissions. Databricks, Fabric and Teams are optional today.

Keep a table: service, resource/region, successful request, denial/error case, result path, cost observation and cleanup. Different services or tenant/region restrictions may prevent some live experiments; mark those unrun.

## 12. Save learning and clean up — final 30 minutes

Download the source, ARM template, sanitized journal, deployment result and screenshots before expiry. Review the dedicated group before deleting anything:

```bash
az resource list --resource-group "$LEARNING_RG" --query '[].{name:name,type:type}' -o table
# Deletes everything in this dedicated learning group; do not substitute an unrelated group.
az group delete --name "$LEARNING_RG" --yes --no-wait
az group wait --name "$LEARNING_RG" --deleted
```

Also inspect services created in other groups, particularly Search, Databricks compute, disks and endpoints. Stopping a web app does not remove its B1 plan charges. Expiry is not a migration or evidence-retention plan.

## Troubleshooting: identify the failing layer

| Symptom | Likely layer | What to inspect or change |
|---|---|---|
| CONNECT 403 before reaching Azure | Codex outbound policy | Apply the precise destination rule; Azure RBAC will not fix proxy rejection |
| AADSTS530035 after browser sign-in | Entra security defaults | Observed in this session. Use Portal-authenticated Cloud Shell and complete any MFA/security registration; if it also fails, have the tenant administrator inspect sign-in logs. Do not disable security defaults |
| Device code no longer works after success screen | Completed or expired device flow | Do not reuse the old code. Check CLI outcome; browser success alone does not prove subscription access |
| Please run az login | Local CLI authentication | Sign in securely; subscription ID alone supplies no access |
| Subscription not found | Account/directory selection | Check az account list and tenant; sign in to the account with access |
| SubscriptionDisabled / expired credit | Subscription billing state | Check Portal offer status; do not silently upgrade billing |
| AuthorizationFailed creating resources | Management RBAC | Verify correct subscription and scoped deployment rights |
| roleAssignments/write denied | Role-assignment rights | Owner/RBAC administrator or approved equivalent must assign the data role; Contributor is insufficient |
| MissingSubscriptionRegistration | Resource provider | Register only the required provider if authorized, then retry |
| RequestDisallowedByPolicy | Subscription/organization policy | Read the specific policy and allowed region/SKU; don't keep retrying unchanged |
| SKU unavailable / quota exceeded | Regional capacity or offer quota | Choose a permitted available region/tier after checking cost; credit cannot override quota |
| App/storage name already exists | Global resource naming | Select a new valid name and update redirect URI/settings consistently |
| InvalidTemplate | ARM schema/expression | Inspect validation details and failing resource/property; no blind retries |
| AADSTS50011 | Redirect mismatch | Match exact HTTPS callback URI and app name in the Entra Web platform |
| AADSTS7000215 | Client secret invalid | Use secret value, correct registration and unexpired secret; enter securely |
| AADSTS50105 or assignment required | Enterprise app assignment | Assign the approved user to the correct role in the correct tenant |
| Sign-in works but app returns 403 | App authorization | Check tenant/object identity and Forecast.User claim; log out/in after role assignment |
| Unsigned-in root returns 401 | Expected platform enforcement | Use /.auth/login/aad, then return to root; don't disable auth |
| Health is 200 but /ask is 503 | Runtime/storage dependency | Inspect startup/deployment logs and managed identity Blob access; health only proves liveness |
| App startup 502/503 / module not found | Package/build/startup | Ensure learning web_api.py is packaged, root requirements installed, correct Gunicorn module |
| Storage 403 AuthorizationPermissionMismatch | Data RBAC or propagation | Verify actual managed identity client ID, Blob role and account; retry after propagation evidence |
| /ask returns 400 | Request schema | Send application/json, bounded message, session_id and request_id; no user identity fields |
| /ask returns 409 | Case/request conflict | Check request reuse, state version and payload; don't retry changed writes under the same ID |
| Duplicate what-if scenario | New IDs on repeated submissions | Use stable IDs for redelivery; inspect existing case before repeating |
| No workspace logs | Diagnostics/ingestion | Check enabled categories, actual traffic, delay and daily ingestion cap; workspace existence is insufficient |
| Model 429 in a separate lab | Model quota/rate limit | Respect Retry-After, reduce calls and check model/region quota; don't loop aggressively |
| Service 404 | Wrong endpoint/model/deployment/API family | Match the actual service and deployment name; a chat model is not an embedding model |
| Speech native import failure | OS/native dependencies | Use a supported host and its documented prerequisites, not a code change that skips recognition |
| Teams upload/admin-consent blocked | Tenant policy/licensing | Continue the working web path; student membership does not grant tenant administration |

Unexpected errors belong in the journal with time, operation, sanitized code and next diagnosis. Do not invent success or copy complete logs containing credentials.
