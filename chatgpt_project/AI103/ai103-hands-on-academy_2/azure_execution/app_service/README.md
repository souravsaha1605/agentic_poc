# Deploy the API to Azure App Service

A long-running web server should not be kept alive inside a lesson notebook.
The course supplies a WSGI API and Bicep; use App Service for this optional hosting exercise.

## Portal resource setup (manual alternative to Bicep)

1. Azure Portal → **App Services → Create → Web App**. Select learning group, globally unique
   app name, Publish=Code, Runtime=Python 3.11, Operating System=Linux, supported region.
2. Create a small paid learning plan (the Bicep example uses B1). Review pricing and deploy.
3. App → **Identity → System assigned → On → Save**. This principal is separate from your notebook app.
4. App → **Configuration / General settings → Startup Command**:
   `python -m gunicorn --pythonpath src --bind 0.0.0.0:8000 --workers 2 --timeout 120 academy.api:application`
5. App → **Environment variables**: add `SCM_DO_BUILD_DURING_DEPLOYMENT=true`, `API_LIVE=false`,
   and a fresh random `API_DEMO_TOKEN` value. Save/restart. Keep the token outside notebooks/widgets.
6. To use Bicep instead, follow [Cloud Shell](../cloud_shell/README.md) and [infra](../../infra/README.md).
   Do not create both sets of resources accidentally.

## Package and deploy from Cloud Shell

After extracting the course in Cloud Shell, run from its root:

```bash
python3 scripts/package_deployment.py
az webapp deploy --resource-group YOUR_LEARNING_RG --name YOUR_APP_NAME --src-path outputs/app-deploy.zip --type zip
```

Replace the two uppercase names. Deployment uses the service build to install requirements.
If startup fails, open **Deployment Center logs** and **Log stream**; check dependency installation
and startup module before changing authentication settings.

Open `https://YOUR_APP_NAME.azurewebsites.net/health`; expect `status=ok`.
For an authenticated smoke test run the provided client in Cloud Shell:

```bash
python3 azure_execution/app_service/smoke.py
```

It prompts for app URL and a hidden token, then checks /health and /ask. No token is printed.
For live RAG add model/safety values in Environment variables or Key Vault references, enable the
app identity's data role on the model, set MODEL_AUTH=entra, then API_LIVE=true. The API uses
local synthetic policy retrieval. To practice Azure Search use lab 11; the API does not
silently switch stores.

## Custom Search skill endpoint

The same deployed app exposes POST `/skill`, protected by the same demo Bearer token.
See [the skill connection exercise](../search_indexer/README.md). This shared token is suitable
only for a private learning deployment with synthetic records. Production deployment requires
validated caller identity, narrower permissions, key rotation and network controls.

## Acceptance and cleanup

/ask and /skill without token must return 401. /ask with valid JSON returns policy evidence.
Invalid JSON must return 400. Redeploy the previous package to practise rollback.
Delete the dedicated app AND its App Service plan after the exercise; stopping the app alone
may not remove provisioned plan charges.
