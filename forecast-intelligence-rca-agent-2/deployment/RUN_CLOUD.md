# One deployment path after access is supplied

The code can be pushed without Azure access. To execute this path, use an
Azure CLI session/Cloud Shell authenticated to the approved subscription, with
resource-deployment and role-assignment permissions. The published Azure OpenAI
key authenticates model calls; it does **not** authorize these management actions.
Databricks workspace/warehouse permissions and tenant app installation are
separate prerequisites.

1. Select the subscription, existing/new resource group and region. Agree unique
   App Service/storage names. Review `azuredeploy.json`: one paid B1 Linux host,
   a dedicated LRS storage account, user-assigned identity, narrow storage RBAC,
   Azure Bot and Teams channel. It creates no OpenAI deployment or SQL warehouse.
2. Ensure the resource group exists. Run the non-mutating review command from
   this folder in your authenticated Cloud Shell (replace uppercase placeholders):

   ```bash
   python deployment/deploy_azure.py --subscription SUBSCRIPTION --resource-group GROUP --location REGION --app-name APP --storage-name STORAGE
   ```

3. After reviewing the actual `what-if` result, run the same command with
   `--execute`. It deploys the template and source ZIP; the cloud build installs
   the Teams dependencies. Optional `--identity-map`, `--privacy-notice`,
   `--terms-notice`, `--acceptance-report` paths include private deployment files.
   Those ZIPs must remain private. No developer state, `.env` or keys are packaged.
4. Initialize the approved `*_lab` database with notebook 01, then run notebook
   02. Fresh v5.2 lab initialization creates the newly certified driver fixtures.
   An existing incompatible v5.1 lab remains unchanged; choose a new lab schema
   or review an explicit schema migration. No enterprise evidence is synthesized.
5. Add the deployed managed identity to the Databricks workspace/account with
   warehouse use and required Unity Catalog grants. Then merge source settings:

   ```bash
   python deployment/configure_runtime.py --subscription SUBSCRIPTION --resource-group GROUP --app-name APP --databricks-host https://WORKSPACE.azuredatabricks.net --warehouse-path /sql/1.0/warehouses/WAREHOUSE_ID --databricks-resource-id /subscriptions/SUBSCRIPTION/resourceGroups/GROUP/providers/Microsoft.Databricks/workspaces/WORKSPACE
   ```

   Existing standard or `MY_AZURE_OPENAI_*` process bindings supply the optional
   model key securely; it is never passed on the command line. Keep the commands
   in the same secure Cloud Shell session where those bindings are available.
6. Verify app health, storage writes, SQL reads, actual source certification and
   owned-case restart/retry. Supply verified canonical identity mappings and
   reviewed privacy/terms files. Carry the original paid-call ledger during
   state cutover. Upload the generated personal Teams app through tenant policy.
7. Run valid/invalid authentication, user/tenant isolation, restart, durable queue
   and proactive delivery tests. Only after the actual tests pass, update the
   restricted acceptance report and enable Teams. Optional LLM ranking remains
   off until a controlled small model test passes.

In this Codex environment, allow the exact published model hostname in Internet
settings, save and publish that change before running:

```bash
python live_validation.py --report /tmp/forecast-live-validation.json
```

This uses the existing ledger and permits at most **three total validation
reservations**, including earlier failed attempts. It stops on the first error,
sends only compact synthetic aggregates, and records actual token usage on
success. It does not silently retry or accept fallback text as a live success.

ARM JSON/package structure can be checked locally; Azure-side template validation
and actual `what-if` remain pending until subscription authentication is supplied.
The full live deployment and Teams tenant checks are not implied by local tests.
