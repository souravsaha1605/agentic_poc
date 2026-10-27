# Azure Databricks execution guide

## 1. Create or select a learning workspace

In Azure Portal, search **Azure Databricks**, choose **Create**, select your subscription,
learning resource group and supported region. Use a workspace/plan with Unity Catalog access.
Review the charge estimate and deploy. Choose **Launch Workspace**. An existing approved
workspace is fine; ask its administrator for a writable catalog/schema and compute permission.
Do not alter your employer's security settings to make a lab work.

Under **Compute**, use a supported classic runtime with Python 3.11 or newer. A small
single-node/dedicated learning compute configuration with auto-termination is sufficient.
Confirm the runtime's Python version in lab 00. Dedicated classic compute is the easiest path
for native Speech libraries and a local MCP subprocess. Serverless/shared configurations can
restrict subprocesses, native libraries or filesystem paths; use the noted alternative when blocked.

## 2. Prepare persistent files

In **Catalog**, select a catalog and schema where you have permissions. Create a managed volume
named `ai103_lab` (or use an existing approved volume). You need USE CATALOG, USE SCHEMA,
READ VOLUME and WRITE VOLUME; creating it additionally requires CREATE VOLUME.
Upload `ai103-hands-on-academy.zip` using the volume's **Upload files** action.
Record `/Volumes/<catalog>/<schema>/<volume>/ai103-hands-on-academy.zip`.

Extract the ZIP on your computer as well so you can read the Markdown files and import individual
notebooks. In **Workspace**, create an `AI103` folder → **Import** → select
`databricks/00_BOOTSTRAP.py` → choose Python/source format if asked. This is a notebook, not
an attempt to execute the whole archive as one notebook.

Set `zip_path` to your uploaded ZIP, and `output_root` to
`/Volumes/<catalog>/<schema>/<volume>/ai103-output`. Attach compute and run bootstrap.
It extracts to `/local_disk0/tmp/ai103-course/ai103-hands-on-academy` on the driver.
This avoids SQLite/native-library issues with object-storage/FUSE paths. The local copy is
EPHEMERAL; re-run bootstrap after a cluster restart. JSON evidence is written to the volume.

## 3. Run one lesson

Import the corresponding `.py` from `databricks/labs/` into Workspace. Read that lab's README.
Keep `live=false` initially. Fill `project_root` with the bootstrap path and `output_root`
with your volume path. Run its cells. For a cloud run, finish the linked Azure setup first,
set `live=true`, and run the package-install and Python-restart cells before the final cell.
Re-run imports/secret loading after a Python restart; Python variables are cleared.

Only the current requirement set is installed. `%pip` installs notebook-scoped packages.
Keep conflicting SDK generations in separate notebook sessions/compute when necessary;
MCP lab 21 deliberately uses v1. Capture `pip freeze` after a successful live environment
and keep it with your evidence. Dependency ranges in this course are compatibility intent,
not a claim that every future release in a range has been cloud-tested.

Use the `variant`, `question` and `input_file` widgets for the experiments described in each
README. When `input_file` points to a volume, the launcher copies it to local driver storage
before calling native SDKs. Generated JSON/PNG/MP4/WAV files go to output_root.

## 4. Secrets through Azure Portal and a Key Vault-backed scope

For this path create a **dedicated learning Key Vault**. In Azure Portal → Key Vault →
**Access configuration**, choose **Vault access policy** for the traditional Key Vault-backed
Databricks secret scope. Do not switch an existing shared vault from RBAC; use a separate vault.
The direct SDK Key Vault lab uses a separate RBAC vault if you want to practice that model too.

In the dedicated vault, create only the secrets needed for the current lab. Secret names are
the environment variable names lowercased with underscores replaced by hyphens, for example:
`azure-openai-endpoint`, `azure-openai-api-key`, `model-small`, `safety-endpoint`, `safety-key`.
The precise per-lab mapping is in `databricks/secret_mapping.json`.

Copy the vault **DNS name / Vault URI** and **Resource ID** from its properties.
Open `https://<your-databricks-workspace-host>#secrets/createScope` (the path is case-sensitive).
Choose scope name `ai103-lab`, the narrowest available management principal, and Azure Key Vault
as the backend. Paste the DNS name and resource ID and create the scope. Creation requires the
Azure permissions documented by Databricks; if denied, ask an administrator to create it.
A successful scope gives readers access to secrets in that scope, so use a dedicated vault.
Verify the intended user has scope read permission. Use `dbutils.secrets.get` in the generated
lesson notebook; never print its return value. Secret redaction is helpful but not a guarantee
against deliberate output/serialization.

If your organization requires RBAC-only vaults, use an administrator-provisioned Databricks-backed
scope, or an approved Unity Catalog external-secrets integration instead. The notebook only
requires a functioning `dbutils.secrets.get(scope, key)` mapping. Do not disable organizational
controls to follow the traditional scope route.

## 5. Azure SDK identity from a Databricks notebook

Most beginner service examples use service-specific keys loaded from the scope. Labs 01, 15
(Cosmos) and 16 use Entra ID. In Azure Portal → **Microsoft Entra ID → App registrations →
New registration**, create a dedicated learning application. Record tenant and client IDs.
Under **Certificates & secrets**, create a short-lived client secret for the exercise, or use
your organization's approved certificate/federation method. Store tenant ID, client ID and
secret as `azure-tenant-id`, `azure-client-id`, `azure-client-secret` in the learning vault.
Assign this principal the required SERVICE DATA roles at narrow resource scope.
The launcher sets AZURE_TENANT_ID/CLIENT_ID/CLIENT_SECRET only in the driver process;
DefaultAzureCredential then uses EnvironmentCredential.

This is a learning credential path. For production Databricks use your approved workload
identity/service credential design and rotate any unavoidable secrets. A Databricks Access
Connector identity used for Unity Catalog storage is not automatically the credential used
by arbitrary Azure SDK calls in your Python process. Test the actual principal and scope.
Do not rely on `az login` in notebooks or assume notebook identity equals workload identity.

## 6. Driver code versus Spark

These examples call Azure APIs from the driver and use small synthetic datasets. Do not put
SDK clients, credentials or unbounded model calls inside UDFs/mapPartitions. A later scale-out
design needs approved executor credentials, bounded concurrency, retry policy, quotas and
idempotent result storage. You can inspect result JSON with Spark after it is written to a volume.

SQLite exercises are in-memory or driver-local. They demonstrate transactions but are not
shared, durable Databricks state. Use the Redis/Cosmos labs or Delta tables with a carefully
designed concurrency model for durable workflows. Do not put a SQLite database in a volume.

## 7. Native and advanced exceptions

Speech requires native runtime support. If the SDK cannot load, use supported dedicated
compute or the Azure VM fallback in azure_execution/native_vm; do not install OS packages on shared compute without approval.
MCP requires a local subprocess; the launcher includes PYTHONPATH for it. The async runner works
inside an existing notebook event loop. Fabric ODBC requires ODBC Driver 18 plus pyodbc; use the
SQL endpoint in Fabric's portal if the driver is unavailable. Azure Portal setup labs remain
portal exercises even when their local code runs on Databricks. App Service hosting is an
optional deployment target; it does not replace the Databricks learning path.

## References

- https://learn.microsoft.com/en-us/azure/databricks/security/secrets/
- https://learn.microsoft.com/en-us/azure/databricks/libraries/notebooks-python-libraries
- https://learn.microsoft.com/en-us/azure/databricks/files/


## Non-secret configuration and extension notebooks

Every launcher has a `config_json` widget for a small allowlist of non-secret overrides.
For a custom analyzer use `{"CU_ANALYZER":"your-analyzer-id"}`; for a new index use
`{"SEARCH_INDEX":"ai103-policies-v2"}`; for Hindi speech use `{"SPEECH_LANGUAGE":"hi-IN"}`.
Do not put keys/tokens in this widget. For keyless chat set `{"MODEL_AUTH":"entra"}` and ensure
azure-tenant-id/client-id/client-secret are available for the learning principal. Image/evaluator examples use key authentication. The reviewed video adapter supports key or Entra authentication.

Advanced variations have separate launchers in `databricks/extensions/`: memory summary, group
discussion, custom enrichment contract and Cosmos vector search. Import them only after their
parent lab. The Cosmos extension needs its vector container created through Portal first.
The REST loopback demo can be run from a separate dedicated notebook; see its README.

## Reviewed edition: exact run behavior

Use classic dedicated compute with Python 3.11+ and Unity Catalog volume support. The first
package-free run tests your paths. Serverless is not the guaranteed baseline for these notebooks.
Every lesson now has RUNBOOK.md. Follow it before generic optional-terminal commands.
Each run creates a new timestamped folder under output_root, and the launcher prints that path.
Do not read an old root-level JSON and assume the latest run succeeded.

Rerun bootstrap after uploading a reviewed ZIP or restarting compute. It replaces only the
course driver copy; save your own experiments in separate workspace notebooks first.
The package install cell and restart cell are distinct. After restart run the final cell.
A settings change takes effect when the final cell executes; non-secret defaults reset each run.

Lab 15 requires redis/cosmos for live mode; lab 30 requires fabric. Local and portal-led lessons
reject live=true with an explanation. Native/portal exceptions are cataloged in
[azure_execution](../../azure_execution/README.md). .env is disabled by the Databricks launcher;
values come from the selected scope and documented non-secret widgets only.

For a first scope, you need the supported Key Vault Contributor/Contributor/Owner permission
and the ability to add access policies. In the access-policy vault, give yourself temporary
secret Set/Get/List permissions to create learning secrets. Databricks scope creation adds its
service Get/List policy. Network settings must permit the documented trusted-service access;
verify the Databricks secrets guide linked above before changing a dedicated vault's firewall.
