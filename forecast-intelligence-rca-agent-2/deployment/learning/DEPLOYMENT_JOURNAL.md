# Deployment journal — forecast RCA learning application

**Last updated:** 12 November 2026, India time (UTC+05:30). Entries describe observed results; planned commands are in MANUAL_WALKTHROUGH.md.

| Item | Current value |
|---|---|
| Authorized subscription | Azure subscription 1 |
| Subscription ID | ba631193-a731-4715-8718-5d0dc3b5917c |
| Remaining balance reported by user | 19000 credits; currency/offer and exact expiry not verified |
| Region | Not selected; allowed region/quota must be checked after authenticated access |
| Main architecture | Entra-authenticated App Service API + managed identity + Blob state + diagnostics |
| Teams | Optional separate learning path; not required for this deployment |
| Deployment state | **Not deployed** |
| Current blockers | Codex Azure CLI remains blocked by security defaults. User-provided Cloud Shell metadata confirms the authorized subscription is Enabled and selected; continue execution in Cloud Shell. |

## Work completed before the live attempt

1. Read the uploaded handbook as reference material. Used its topics to select service labs; did not treat document text as execution instructions or independent evidence of current exam coverage.
2. Inspected repository components. Kept forecast RCA as the main application, as requested.
3. Added a Teams-independent browser/HTTP adapter and source-only deployment package builder.
4. Added single-tenant Entra platform-authentication settings plus application tenant/object/Forecast.User role checks. No shared-token bypass.
5. Reused the deterministic conversation/tool layer. Explicit synthetic records and zero model calls remain the learning web path.
6. Configured the new ARM template for B1 Python hosting, user-assigned managed identity, private Blob state, Blob data RBAC and Log Analytics diagnostics. Did not create a model, Search, Key Vault, Databricks or Teams resources.
7. Tested 110 forecast cases: 95 passed, 15 optional integration cases skipped. The seven new HTTP/package tests are included in that total.
8. Extracted the source ZIP into a clean temporary directory. Started two Gunicorn workers and verified real local HTTP health, denial, page, analysis and replay with simulated platform identity. No Azure token or Blob access was implied.
9. Ran the academy's 51 unit tests and all 37 offline lessons/capstones successfully. Added a no-Databricks launcher for four selected service labs. Live service calls are unrun.
10. Prepared an uploadable source archive and separate deployable ZIP. Changes have not been pushed to GitHub.

## Live access attempt — approximately 17:29–17:31 IST

| Step | Action actually taken | Observed result | Interpretation / manual equivalent |
|---|---|---|---|
| 1 | Checked CLI availability | az executable initially absent | Tool prerequisite missing, not an Azure authorization failure |
| 2 | Inspected configured Azure identity metadata and required variable presence, without values | Identity connection list empty; no client/tenant/federated-token binding | No configured Azure identity was available; subscription ID does not authenticate |
| 3 | Read current environment policy/status | Restricted outbound access enforced; no custom Azure destinations | Need explicit endpoint access from this executor |
| 4 | Sent HTTPS HEAD probes to management.azure.com and login.microsoftonline.com | CONNECT tunnel failed, HTTP 403 from proxy | Destination policy rejected the requests before Azure authentication; this is not an Azure RBAC error |
| 5 | Read the current editable draft and preserved preset network access | No existing custom destination rules | Safe to add the required management/authentication destinations without replacing unknown rules |
| 6 | Saved network draft additions | status=saved; requires_publish=true | management.azure.com, login.microsoftonline.com and graph.microsoft.com added to draft. Save did not apply/publish runtime changes |
| 7 | Installed Azure CLI in an isolated user-owned virtual environment | Installation completed; az version reports 2.92.0 | CLI is now usable locally without modifying app dependencies |
| 8 | Ran az account show for the exact subscription with an isolated CLI config directory | ERROR: Please run 'az login' to setup account | No authenticated CLI session; do not attempt resource mutation |
| 9 | Wrote detailed manual walkthrough, troubleshooting and this journal | Files available locally | User can use Cloud Shell while Codex access is being configured |

CLI location: `/workspace/.venvs/azure-cli/bin/az`. Session configuration location: `/workspace/.azure-learning`. This directory may contain authentication cache after sign-in; it is outside the source archive and must never be exported as learning evidence.

## Exact read-only account check

```bash
AZURE_CONFIG_DIR=/workspace/.azure-learning /workspace/.venvs/azure-cli/bin/az account show --subscription ba631193-a731-4715-8718-5d0dc3b5917c --query '{id:id,tenantId:tenantId,state:state}' -o json
```

Observed authentication failure is above. No account, tenant access, region quota or expiry details were returned. No resource group, registration or role assignment has been created by this session.

## Network update and sign-in attempt — approximately 17:33 IST

- Refreshed runtime status: revision 2, observations current, unrestricted outbound network policy enforced. This change was observed in the runtime; the agent did not request unrestricted access in its earlier three-domain draft.
- Fresh HTTPS probes now reach both destinations: management root returned an Azure HTTP 400 for the root probe (connectivity established, not authenticated success); Microsoft login returned HTTP 200.
- Started `az login --use-device-code --output none` with the isolated config directory. Microsoft returned its official device sign-in URL and a short-lived code, which was shown only for the user to complete login.
- The user completed the browser sign-in step. Subsequent CLI subscription discovery failed as recorded below. No credentials are stored in this journal. No resources have been created.

## What must happen next

1. Network connectivity is now verified. Preserve the intended network policy in environment settings; the earlier draft save alone was not evidence of applied access.
2. Establish secure Azure sign-in for this executor, or use already authenticated Azure Cloud Shell. Never send password/token/client-secret values through chat. A subscription identifier alone cannot establish this connection.
3. Query the authenticated subscription, directory, permissions, allowed regions and quota. Choose a supported region and record exact expiration. These facts cannot be inferred from the subscription name.
4. Create/configure the single-tenant app registration and Forecast.User assignment in the correct directory. Directory permissions are separate from Azure resource RBAC.
5. Run Azure template validate and what-if; review the actual operations/costs, then deploy the already-authorized learning footprint if prerequisites pass.
6. Add only exact app/SCM/Blob destinations needed for actual resulting resource names when using Codex's restricted networking. Application-site deployment connectivity is distinct from management access.
7. Run every live acceptance check and append concrete results below. Do not label the app deployed or production-ready based on the local test suite.

## Live acceptance record — pending

| Check | Status | Evidence required |
|---|---|---|
| Authenticated subscription and correct directory | Unrun / blocked | Safe account metadata |
| Supported region and B1 quota | Unrun / blocked | Actual subscription validation |
| Azure-side template validation and what-if | Unrun / blocked | Successful validation and reviewed changes |
| Infrastructure provisioning | Unrun / blocked | Deployment state and resource inventory |
| Entra sign-in / role denial | Unrun / blocked | Assigned and unassigned user outcomes |
| Blob managed-identity reads/writes | Unrun / blocked | Successful actual forecast request plus persisted follow-up |
| Duplicate replay and app restart | Unrun / blocked | Stable request replay and context after restart |
| Log delivery | Unrun / blocked | Actual application and workspace records |
| Live AI-103 service calls | Unrun | Per-service request/response evidence and costs |
| Export and cleanup | Unrun | Retained sanitized artifacts and verified resource removal |

## Evidence rules

Retain times, operation names, error codes, deployment IDs and sanitized outputs. Keep credentials, cookies, tokens, full principal headers and identity caches out of screenshots, archives and logs. Distinguish an actual observed error from a troubleshooting hypothesis. Append results after actions occur, not in anticipation of success.

## Device sign-in result — 12 November 2026, 17:34:41 IST

The Microsoft browser page reported successful sign-in. The Azure CLI process then exited with code 1 during tenant/subscription discovery:

```text
AADSTS530035: Access has been blocked by security defaults.
Tenant: a71e922d-d0ad-4933-b2a7-201574b5c151 (Default Directory)
Trace ID: 82a821d9-bbb0-4190-8f49-9e45c22b4f00
Correlation ID: 8efa23e7-086b-4cca-b59e-c90bd8776c90
Azure event timestamp: 2026-11-12 12:04:41 UTC
```

A fresh read-only account check for the authorized subscription still returned `Please run az login`. The CLI also printed `No subscriptions found` after the tenant authentication error. That message does not establish that the subscription is absent, expired or out of credit: tenant access failed first. No Azure management identity was established.

The user's second attempt to enter the earlier device code returned `That code didn't work`. The code was no longer usable after the completed browser sign-in; the screenshots alone cannot distinguish consumed-code and expired-code behavior. The actionable blocker is the directory's security-defaults denial, not code spelling. Do not issue repeated equivalent device logins or disable security defaults.

### Supported next attempt: Portal Cloud Shell

1. Sign in to Azure Portal using the account with subscription access. Complete any Microsoft MFA/security-registration prompts.
2. Switch to the directory containing Azure subscription 1.
3. Open Cloud Shell → Bash. Use its Portal-authenticated session; do not run the same device-code login there.
4. Execute the read-only commands below. Share only the selected metadata or sanitized error, never tokens or credentials.

```bash
az account list --query '[].{name:name,id:id,tenant:tenantId,state:state}' -o table
az account set --subscription ba631193-a731-4715-8718-5d0dc3b5917c
az account show --query '{name:name,id:id,tenant:tenantId,state:state}' -o json
```

If Cloud Shell also fails, record its exact sanitized error and time. A tenant administrator can inspect Entra sign-in logs using the timestamp, trace and correlation IDs above; additional directory/security registration may be required. The Codex executor currently has no browser-interaction tool for an alternative interactive browser login, and no connected Azure workload identity. This limits direct execution here; it does not prevent the manual Cloud Shell deployment path when that session authenticates successfully.

## User reported Cloud Shell commands executed

The user reports running the three subscription-selection commands in Cloud Shell. Their output has not yet been supplied, so Cloud Shell authentication, selected subscription and subscription state remain unverified. A fresh account check in the Codex executor still returned `Please run az login`. Cloud Shell authentication is separate and does not transfer credentials to this executor. Next: review the final account metadata/error, then continue deployment in the authenticated Cloud Shell session if confirmed.

## Cloud Shell authentication confirmed from user-provided metadata

The user supplied actual `az account show` output. It reports AzureCloud, subscription `ba631193-a731-4715-8718-5d0dc3b5917c` (Azure subscription 1), `state=Enabled`, `isDefault=true`, tenant/home tenant `a71e922d-d0ad-4933-b2a7-201574b5c151`, and `cloudShellID=true`. This confirms the user's Cloud Shell session selected the intended enabled subscription. It does not establish remaining credit, exact expiry, resource-deployment/role-assignment rights, regional B1 quota, or credentials in the Codex executor.

Next manual batch: upload/extract the updated source archive, query B1 Linux regions and register the single-tenant forecast app/Forecast.User role. No infrastructure creation has been reported yet.

## Source, region and Entra authorization prepared

These steps establish a reproducible source version and the user identity boundary before infrastructure deployment. The application must know both **who authenticated** and **whether that identity has the Forecast.User role**. Authentication alone does not authorize forecast access.

| Step | Why it is required | Action and observed result | What it proves |
|---|---|---|---|
| Git source selection | Tie the deployment to a reviewable source revision | Cloned `feat/forecast-azure-learning`; `git rev-parse --short HEAD` returned `530553c` | Cloud Shell has the expected deployment code |
| App Service region discovery | Avoid guessing whether the B1 Linux SKU is offered in a region | `az appservice list-locations --sku B1 --linux-workers-enabled` included Central India | B1 Linux is listed in Central India; template validation must still check this subscription's policy/quota |
| Single-tenant app registration | Restrict sign-in to the subscription's Entra directory | Registered `Forecast RCA learning` in Default Directory | An application identity exists for the browser sign-in boundary |
| Client and tenant identifiers | Bind App Service Authentication to the exact application and issuer | Client ID `922ccd1b-86d7-4e0a-87e8-9e1b97bdadc9`; tenant ID `a71e922d-d0ad-4933-b2a7-201574b5c151` | The non-secret identity parameters are known for the ARM deployment |
| App role | Separate successful sign-in from authorization | Created enabled role value `Forecast.User` for Users/Groups | The application can require a specific authorization claim |
| User assignment | Put the learning user into the allowed role | Individual user assignment succeeded | The assigned user should receive `Forecast.User` after a fresh sign-in once App Service Authentication is configured |

The portal warned that group assignment is unavailable at the current Entra plan level. Individual assignment remains supported and succeeded, which is sufficient for this single-user lab. No directory upgrade is required. Group-based enterprise access remains a documented production consideration.

This does **not** yet prove application sign-in, role-claim delivery, App Service deployment, Blob access or runtime authorization. Those require the redirect URI, App Service authentication configuration and live acceptance tests.

## Git-based delivery preparation

The user explicitly authorized creating and pushing a feature branch. Created local branch `feat/forecast-azure-learning` from the existing checkout without resetting or replacing user work. Re-ran the forecast suite: 110 tests, 95 passed and 15 optional skips; academy suite: 51 passed. Updated source-transfer instructions to clone this branch and record the deployed commit SHA. Source archive upload is now an optional fallback. Push outcome is verified separately by checking the remote ref; branch creation alone does not prove remote access or deployment.

## Global Azure resource names checked

Name availability is checked before configuring the Entra callback because the callback contains the final App Service hostname. Storage and App Service names are globally scoped across Azure, so a valid local name can still be unavailable.

| Resource | Proposed name | Read-only check | Observed result |
|---|---|---|---|
| App Service | `forecast-rca-922ccd` | Microsoft.Web `checknameavailability` through `az rest` | `nameAvailable: true` |
| Storage account | `forecastrca922ccd` | `az storage account check-name` | `nameAvailable: true` |

The checks do not reserve either name. Another Azure customer could claim a name before deployment. The exact Entra Web redirect URI can now be configured as `https://forecast-rca-922ccd.azurewebsites.net/.auth/login/aad/callback`. No Azure infrastructure creation has been reported at this point.

## Next controlled checkpoint

Before provisioning the paid B1 plan, verify the exact Web redirect URI is present on the existing app registration. Then create the dedicated resource group and run `az deployment group validate`. A resource group is the lifecycle and access boundary for this exercise; it has no provisioned compute charge by itself. ARM validation evaluates the template against the selected subscription, region, resource providers, policy and the operator's permissions. Validation success still does not create the application or prove runtime behavior; deployment `what-if` follows next.

## Azure what-if reviewed

The user ran the group deployment what-if against `rg-forecast-learning`. Azure predicted **11 creates**, with no modifications or deletions. The generic warning about possible what-if noise was present, but the predicted resource set matched the reviewed template.

| Predicted resource | Relevant reviewed properties | Why it is present |
|---|---|---|
| User-assigned identity `forecast-rca-922ccd-identity` | Central India | Keyless workload identity for Blob access |
| Log Analytics `forecast-rca-922ccd-logs` | PerGB2018, 30-day retention, 0.1 GB/day ingestion cap | Bounded operational log retention; quota is not a total-spend cap |
| Storage `forecastrca922ccd` | Standard_LRS, HTTPS/TLS 1.2, public Blob disabled, shared key disabled, OAuth default | Private durable application state without account keys |
| Blob service/container | Versioning enabled, 7-day soft delete, `forecast-rca-state` public access None | Recoverable private state container |
| Blob data role assignment | Role GUID `ba92f5b4-2d11-453d-a403-e96b0029c9fe` for the managed identity | Storage Blob Data Contributor for the dedicated state account |
| Linux App Service plan | B1, capacity 1, Central India | Paid application compute baseline |
| Web app `forecast-rca-922ccd` | Linux, HTTPS-only, client affinity disabled | Hosts the Python API and browser interface |
| App Service Authentication | Required, unauthenticated action Return401, only `/health` excluded; exact client/tenant/audiences | Single-tenant user-authentication boundary |
| App logging and diagnostic setting | Console and HTTP logs enabled and routed to the workspace | Runtime troubleshooting and evidence |

No Bot/Teams, OpenAI/model, Databricks, Search, Key Vault, Cosmos DB, queue, or Application Insights resources were predicted. The role is scoped to the dedicated Storage account, which currently contains only the state container; a larger shared account should use a narrower container scope. The B1 plan begins accruing charges after creation, and workspace/storage usage can also incur consumption charges. What-if does not reserve names, prove deployment success, configure the Entra client secret, deploy application source, or validate runtime behavior.

**Review decision:** the predicted changes are consistent with the authorized learning architecture. The next mutation is the actual ARM group deployment. After infrastructure succeeds, configure the App Service authentication secret securely, build/deploy the source ZIP, and run live acceptance checks.

## Infrastructure deployment succeeded

The user reported that `az deployment group create --name forecast-web-infra` completed with provisioning state `Succeeded`. This establishes that Azure accepted and provisioned the reviewed infrastructure in `rg-forecast-learning`. The B1 App Service plan is now a running billable resource even if the web application has not yet received its source package.

This success does not by itself prove that all data-plane operations or application paths work. The next gates are:

1. Create a short-lived Entra client secret and place its **value** only in the App Service setting named `MICROSOFT_PROVIDER_AUTHENTICATION_SECRET` through the Portal's secure editor. Never put it in Git, chat, screenshots, shell history or the deployment package.
2. Build the deployment ZIP from the recorded Git commit and deploy it to App Service.
3. Verify public liveness, required sign-in, role authorization, managed-identity Blob writes, request replay, restart persistence and actual log delivery.

The reported success has not yet been supplemented with a resource inventory or runtime acceptance evidence. Those remain pending rather than inferred from ARM provisioning.

## First source deployment failed at Kudu

The first `az webapp deploy --type zip` attempt reached and warmed the Kudu deployment service, then failed when the deployment API returned HTTP 502. Azure reported runtime `PYTHON|3.12`, region Central India, plan B1, stage Unknown, and last step "HTTP request sent to deployment API." No successful source release or application acceptance is claimed.

The CLI also displayed a generic warning that Linux build automation is off by default. The reviewed ARM template already sets `SCM_DO_BUILD_DURING_DEPLOYMENT=true`; this must be verified on the live app through a filtered, non-secret app-setting query. The warning alone is not treated as the root cause. HTTP 502 can represent a transient Kudu/control-plane problem or a service-side failure; retrying unchanged before reading the latest deployment log would lose diagnostic discipline.

Next read-only diagnostics:

1. Query web-app state and availability.
2. Query only the non-secret `SCM_DO_BUILD_DURING_DEPLOYMENT` setting; never list all settings because the authentication secret is present.
3. Read the latest Kudu deployment log through `az webapp log deployment show`.

Runtime log streaming follows only if the deployment log shows that source extraction/build/startup began. A single fresh retry is reasonable only after the evidence indicates a transient Kudu 502 or after a concrete configuration correction.

### Initial Kudu log evidence

The latest deployment log identified deployment `adb217e3-1d38-4803-ae27-4dd9293ccec0`. It recorded submodule update, deployment preparation, output path `/home/site/wwwroot`, extraction path `/tmp/zipdeploy/extracted`, and finally `Running oryx build...`. This proves the ZIP reached Kudu, was extracted, and build automation began. Therefore the earlier CLI warning that Linux builds are disabled by default is not the observed failure cause.

The supplied log stopped at Oryx build start and contained no success/failure completion record. The client-side 502 may have interrupted status reporting while the server-side operation continued. Before any retry, query the deployment list/current status, re-read the same deployment ID after it has settled, and probe the public `/health` endpoint. If `/health` returns the expected JSON and the deployment status is successful, the CLI 502 was a client/control-plane reporting failure rather than a failed release.

### Public liveness probe timed out

A later `curl --include --max-time 30 https://forecast-rca-922ccd.azurewebsites.net/health` returned curl error 28 after 30 seconds with zero response bytes. Therefore the app is not accepted as live and the source release is not considered successful. Because `/health` is excluded from Easy Auth, this result should be correlated with the web-app state, the settled deployment status, configured runtime/startup command and application log stream before changing authentication or retrying the ZIP.

The timeout alone does not identify the root cause. Candidate layers include an unfinished/failed Oryx build, unavailable worker, dependency/startup failure, or request-path connectivity. Read-only state and logs are the next checks. No repeated deployment should be attempted until they distinguish these cases.

## Cloud Shell session recovery

After a disconnect, the new Cloud Shell opened in the user's home directory and `~/agentic_poc-azure-learning` was absent. Consequently `git pull`, the component `cd`, and `git rev-parse` failed before any Azure operation ran. This is a local Cloud Shell workspace issue, not a source-control, application or Azure deployment failure. Recovery instructions now search the home filesystem first and re-clone `feat/forecast-azure-learning` only when no existing checkout is found. Deployment variables must be exported again because shell variables are process-local.

The playbook now explicitly separates the temporary Cloud Shell checkout from the production code lifecycle. GitHub is the canonical source; a tested immutable ZIP or container is the deployable artifact; App Service holds the runtime copy; Blob Storage holds durable application state. Re-cloning is not part of normal application runtime behavior. A production CI/CD identity would perform packaging and deployment without relying on a developer's Cloud Shell filesystem.

### GitHub push confirmed

`git push -u origin feat/forecast-azure-learning` succeeded and created the remote branch in souravsaha1605/agentic_poc. The implementation commit is `e92ce7c`. A following documentation commit records this confirmed result. Clone the feature branch in Cloud Shell and record its current full HEAD before deploying. GitHub push success does not supply Azure management authentication or deploy any resources.
