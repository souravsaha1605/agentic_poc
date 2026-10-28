# Consolidated Azure and Databricks setup after code review

No Azure resources were provisioned by this change. Live model, Genie, tenant
authentication and Teams delivery checks are deliberately deferred. Complete
these steps in order; keep both integrations disabled until their gates pass.
Do not send keys in chat or put them in Git/notebook cells.

## 1. Prepare the Databricks lab and source permissions

1. Use an existing supported Databricks Runtime with Delta. Sync this folder,
   install `requirements.txt`, and set `FORECAST_PROJECT_DIR` to this folder if
   the notebook working directory differs.
2. Set `FORECAST_DATABASE=workspace.forecast_rca_lab`, or another dedicated
   `*_lab` schema. The supplied initializer rejects enterprise schemas.
3. Give the controlled initialization identity schema/table/view creation and
   maintenance privileges in that lab only. Run `01_data_initialization.ipynb`,
   then `02_golden_rca_tests.ipynb`. Preserve any existing source data. Missing
   columns require an explicit migration or a new lab schema, not a forced reset.
4. Give the runtime service identity only the approved views, dimensions,
   source manifest/readiness and source history read privileges it needs. Give
   state/ledger writes to the notebook identity in the dedicated state tables.
   The Azure worker uses Blob state and a SQL warehouse, not notebook Spark.
5. Deploy `deployment/databricks.yml` with an approved existing cluster. This is
   the one maintained readiness job. Run it manually first; agree its schedule
   with the data/budget owner. It audits actual source data and publishes a
   consistent source version after golden tests and feature creation.
6. Create/reuse a small SQL warehouse with a 30-second statement timeout, bounded
   concurrency and auto-stop. Provide an approved Databricks unified-auth binding
   for the Azure managed identity/service principal. Grant only this lab's data.
   Confirm `DATABRICKS_SERVER_HOSTNAME`, `DATABRICKS_HTTP_PATH`, and unified-auth
   settings such as `DATABRICKS_HOST` and the selected OAuth identity. Prefer
   workload identity/managed identity over a PAT.

The new source contract includes explicit `currency`, `discount_unit`, forecast
origin/horizon and inventory timestamp columns. It does not silently assume
currency, reinterpret discounts, copy P001 into P0001, or overwrite an old schema.
Enterprise ingestion, business fiscal calendars and additional external drivers
need reviewed data contracts; this initializer only creates certified lab data.

## 2. Verify user identity and owned session mappings

Copy `deployment/identity-map.example.json` into restricted deployment storage;
never commit real user mappings. For each approved user, create entries for:

- `databricks:ACTUAL_CURRENT_USER_LOGIN`, obtained with `SELECT current_user()`;
- `ENTRA_TENANT_ID:ENTRA_OBJECT_ID`, obtained from verified tenant identity.

Both entries must point to the same canonical `principal` and application
`session_id` **after an operator verifies the account linkage**. Record the
verification provenance and set `verified=true` only then. Supply explicit
regions, products and categories; empty lists deny access. Use `*` only for an
approved global grant. Set `IDENTITY_MAP_FILE` to the restricted file path.
Never authorize using display name, email text, conversation ID or a chat-supplied
user_id. The example file remains unverified and cannot admit a user as supplied.

For notebook development, use Delta state and its shared paid-call ledger:
`create_core('spark', 'delta', spark=spark)`. If changing schema, also configure
`FORECAST_STATE_TABLE` and `FORECAST_BUDGET_TABLE` consistently. Serialize initial
session creation in the notebook host. Multi-worker hosting uses Blob ETags.

## 3. Optional Azure OpenAI configuration

Reuse an existing Azure OpenAI resource and deployed model. Configure securely:

| Setting | Value |
| --- | --- |
| `AZURE_OPENAI_ENDPOINT` | HTTPS base URL including `/openai/v1/` |
| `AZURE_OPENAI_DEPLOYMENT` | Exact deployment name, no guessed default |
| `AZURE_OPENAI_API_KEY` (or `MY_AZURE_OPENAI_API_KEY`) | Secure runtime/Key Vault binding; never a code value |
| `ENABLE_LLM` | `false` initially; `true` only for a controlled optional test |
| `MAX_PAID_CALLS` | `70` or a lower number |

The platform onboarding proxy reserves `AZURE_` secret-target names. If using
that proxy, arrange the supported secure runtime binding in environment settings
rather than trying to declare a reserved proxy-secret target. In App Service,
use secure app settings/Key Vault references under the existing application name.
Allow only your exact Azure endpoint hostname through the environment/network
policy. Do not disable TLS verification. The key is never needed for offline
acceptance or ordinary deterministic analytical work.

A controlled opt-in test may rank existing evidence. Inspect the shared ledger
before and after it. SDK retries are disabled. A failed HTTP attempt consumes one
reservation. The code does not silently retry, increase prompts or switch models.

## 4. Direct Genie pilot and optional application validation

Direct business-user Genie access is independent of the Teams application and
the application-side adapter below. Run `01_data_initialization.ipynb`, then
`03_genie_space_setup.py`, and configure a Genie Space with only
`workspace.forecast_rca_lab.vw_genie_forecast_observations`. Use the reviewed
instructions in `genie/SPACE_INSTRUCTIONS.md`. This does not change
`TEAMS_ENABLED`, the bot route, queues, state, or the future Teams-to-Databricks
SQL path.

The following adapter is only for comparing Genie output inside the custom
application. It remains disabled until its separate authentication and paid-call
controls are approved.

Keep `GENIE_MODE=off` unless the policy owner explicitly approves generated-query
execution in a **synthetic-only** Genie space and warehouse. Grant no enterprise
views to that validation space. Genie Code is a coding assistant; this adapter
uses the separate Genie conversation API.

Construct `GenieHTTP(workspace_host, config.authenticate)` from the supported
Databricks SDK `Config`, then `GenieValidationAdapter(..., approved_spaces=(id,),
mode='validation')`. Pass the same principal, owned session store and paid-call
ledger as the core. `begin` saves provider conversation/message IDs; `poll` is
bounded to at most five HTTP requests and 30 seconds per invocation. Follow-ups
reuse that user's provider conversation; new app sessions get new conversations.
An unknown POST outcome is not blindly retried. Candidate comparisons never
replace deterministic facts, and raw Genie text/SQL/rows never enter core facts.
Review candidate aggregate metrics separately through `compare`.

## 5. Provision the small Teams host

Reuse the existing Databricks/OpenAI resources. Create/reuse:

1. One Linux App Service plan/app with Python 3.12, HTTPS-only and Always On. The
   plan has a paid baseline. One process runs the endpoint and serial worker.
2. One StorageV2 account with HTTPS/TLS 1.2, public Blob access disabled, a private
   Blob container for state/evidence/ledger, one command queue, and one poison
   queue. Apply approved region, encryption, firewall and retention policies.
3. A managed identity for the app. Grant Blob Data Contributor and Queue Data
   Contributor only on the selected state resources. Grant the approved
   Databricks runtime access separately; it does not inherit user entitlements.
4. An Azure Bot registration and supported Microsoft 365 Agents SDK connection
   using the selected identity/auth type. Enable its Teams channel. Set the
   messaging endpoint to `https://YOUR_HOST/api/messages`.

Install `requirements-cloud.txt` in the app build environment. Deploy this
folder as the application root, including the installed dependencies. A suitable
startup command is `python -m channels.host`; port is `8000` unless `PORT` is set.
Use your approved App Service build pipeline to install the cloud requirements,
not just the smaller offline `requirements.txt`. Do not enable a public anonymous
bot route. `create_app` uses the SDK JWT middleware before handling an activity.

Configure these non-secret settings and secure authentication bindings:

| Setting | Meaning |
| --- | --- |
| `CHANNEL_MODE` | `development` until release gates pass |
| `TEAMS_ENABLED` | `false` until release gates pass |
| `GENIE_MODE` | `off` by default; independent of Teams |
| `FACTS_PROVIDER` | `deterministic` (only implemented authoritative provider) |
| `FACTS_BACKEND` | `sql` for governed Databricks; explicit `lab` only for a certified synthetic demo |
| `STATE_BACKEND` | `azure` in the hosted composition |
| `STATE_BLOB_ACCOUNT_URL` | Exact HTTPS Blob service URL |
| `STATE_BLOB_CONTAINER` | Existing private container name |
| `QUEUE_ACCOUNT_URL` | Exact HTTPS Queue service URL |
| `QUEUE_NAME`, `POISON_QUEUE_NAME` | Existing queue names |
| `BOT_CLIENT_ID`, `BOT_TENANT_ID` | Registered identity/tenant |
| `BOT_AUTH_TYPE` | Supported `UserManagedIdentity`, `SystemManagedIdentity` or `ClientSecret` |
| `BOT_CLIENT_SECRET` | Secure binding only if the selected auth type needs it |
| `IDENTITY_MAP_FILE` | Restricted verified account map |
| `TEAMS_ACCEPTANCE_REPORT` | Restricted completed gate report path |
| `FORECAST_DATABASE` | The certified database used above |
| Databricks/OpenAI settings | As described in preceding steps |

For managed-identity Bot registration, match the Azure Bot registration's
application type, identity and tenant to the SDK configuration. Do not mix a
single-tenant client-secret registration with a different managed identity.
Network access is needed only for the exact Databricks, identity, Bot/Teams,
Storage and optional model endpoints. Keep package registry access in the build
phase. Do not broaden egress to all hosts to fix an authentication issue.

The service supports only allowlisted **personal chats**. Acceptance means the
command was durably queued before acknowledgment. The worker rechecks current
identity grants, saves the result first, then sends a proactive SDK response.
Redelivery uses stable request IDs and a saved notification receipt. Sending a
reply successfully and crashing before recording that send can still cause a
duplicate notification. After five failures, accepted work is preserved in the
poison queue. A single instance can pause during a restart; this is not HA.

## 6. Cut over state, package Teams and run release gates

1. Pause notebook/channel writers. Export selected owned sessions with
   `state_migration.export_sessions`. Import into the empty Azure store using
   `import_sessions`; verify owner, session/case counts, version chains and
   checksums. Keep the private source archive for controlled rollback.
2. Carry the **spent paid-call count** to the absent/unused target ledger with
   `transfer_paid_budget`; verify it before enabling any model or Genie call.
   Freeze the old ledger/writer. Do not run both state stores or independent
   budgets for the same project. Rollback also needs the latest paid-call count,
   not an older counter from a pre-cutover snapshot.
3. Use `deployment/package_teams.py` with the real app/bot IDs and public host
   to create a valid personal-app manifest ZIP. Submit it through the tenant's
   approved app upload/installation process.
4. Run the original journeys, real valid/invalid JWT tests, tenant/user denial,
   group-chat rejection, restart/duplicate delivery, async replies, retention and
   state-cutover checks. Cloud tests were **not executed** by this local change.
5. Copy `deployment/acceptance-gates.example.json` into restricted settings and
   attest each gate only after its real test passes. Set `TEAMS_ENABLED=true`
   and `CHANNEL_MODE=teams` only then. A completed report without real tests is
   not a deployment validation result.
6. Verify one small live interaction and its actual usage/ledger change. Keep
   `ENABLE_LLM=false` if deterministic responses meet the need.

Disabling Teams stops admissions and preserves saved cases and queued work. An
already-running worker can finish accepted work; a restart while disabled pauses
it until controlled recovery/re-enablement. Restore only from verified archives;
never guess user identity or clear state/budgets to resolve a deployment error.
Agree the retention period, archive/deletion operator, data/AI/platform owners,
residency, source freshness, support hours and budget owner before release.

Before packaging/tenant submission, configure `PRIVACY_NOTICE_FILE` and
`TERMS_NOTICE_FILE` with your reviewed organizational notices. The host serves
them as plain text at `/privacy` and `/terms`; absent notices return 503 rather
than inventing retention terms. Verify these URLs and the packaged icons during
the tenant's manifest validation.

For an interview or development deployment without an externally accessible
Databricks SQL warehouse, set `FACTS_BACKEND=lab`. This keeps Azure Blob state,
queues, Teams authentication and the full analytical/conversation services, but
reads the versioned BRD fixtures bundled with the application. The application
never falls back to this mode automatically. Label such a deployment as a
certified synthetic demo. Switching to `sql` requires the reviewed Databricks
settings, source manifest/readiness, warehouse access and managed-identity grants.

Legacy shared `demand_planner` records are not automatically assigned to a new
user. The new owned-state tables preserve their source tables but do not guess
ownership. If retaining legacy history, an operator must verify its owner and
convert it to the reviewed archive contract before importing. Never attach the
last globally saved case to a newly authenticated user.

Executable deployment/packaging commands and their access prerequisites are in
[deployment/RUN_CLOUD.md](deployment/RUN_CLOUD.md). The v5.2 source contains
certified synthetic weather, competitor, lifecycle, mix, regional, fiscal and
channel fixtures; these do not substitute for enterprise source evidence.
