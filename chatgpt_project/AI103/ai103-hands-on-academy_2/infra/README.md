# Explicit learning deployment

The template creates a billable B1 Linux App Service plan/app, managed identity, RBAC Key Vault,
Log Analytics and Application Insights. It does not provision Databricks, AI model deployments,
private endpoints or role assignments. Configure those through the incremental setup guides.
Bicep source is provided for review; compilation/deployment requires Azure CLI/Bicep in your environment.

From Azure Cloud Shell (Bash), upload this infra folder or use a local authenticated CLI:

```bash
az group create --name rg-ai103-learning --location <approved-region>
az bicep build --file infra/main.bicep
az deployment group what-if --resource-group rg-ai103-learning --template-file infra/main.bicep
az deployment group create --resource-group rg-ai103-learning --template-file infra/main.bicep
```

Review what-if and pricing before the create command. Record the appName output. In Azure Portal
→ web app → Environment variables, securely configure API_DEMO_TOKEN. Keep API_LIVE=false for
first smoke checks. Give the app identity access to Key Vault/model resources only as needed.
The RBAC vault from this template is not automatically a traditional Databricks secret-scope vault.

Package from the course root:

```bash
python scripts/package_deployment.py
az webapp deploy --resource-group rg-ai103-learning --name <appName> --src-path outputs/app-deploy.zip --type zip
```

The package excludes .env, notebooks, outputs, credentials and the source handbook. Azure's build
uses root requirements.txt. Verify `/health`, then POST `/ask` with JSON `{"question":"return policy"}`
and `Authorization: Bearer <your-demo-token>`. Use a secure API client without printing the token.
The API uses only the synthetic local policy corpus; live=true adds model/safety calls. To use
Azure Search in the API, wire the tested lab 11 retrieval path explicitly and narrow query roles.

For live hosted calls configure model/safety settings in the portal or Key Vault references.
MODEL_AUTH=entra uses managed identity for model inference. Other service key examples still
need their own settings. No real customer data/actions are exposed by this API.

Rollback by redeploying a previously validated package and matching prompt/model configuration.
The basic plan does not supply all staging-slot options; choose an appropriate tier if adding slots.
Remove the plan when finished to stop its ongoing provisioned charges.
