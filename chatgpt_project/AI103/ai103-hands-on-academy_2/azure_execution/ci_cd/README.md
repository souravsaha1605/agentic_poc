# CI/CD configuration in Azure Portal and GitHub

CI executes on a GitHub-hosted runner, not in a Databricks notebook. A GitHub account/repository
is required for this optional exercise; Azure Portal cannot configure repository settings.

1. Create a private repository and upload this course, including `.github/workflows/`. Never
   upload .env or outputs containing customer data. Commit the source, prompts, schemas and tests.
2. In Azure Portal create a dedicated app registration for deployment. Under **Certificates &
   secrets → Federated credentials → Add**, choose GitHub Actions, enter owner/repository,
   entity type Environment, and environment name `learning` (matching deploy.yml).
3. Assign its service principal a deployment role scoped to the learning Web App/resource group,
   such as Website Contributor where sufficient. Do not grant subscription Owner for convenience.
4. GitHub → Settings → Environments → create `learning`; add any available reviewer protection.
   Add repository/environment variables AZURE_CLIENT_ID, AZURE_TENANT_ID,
   AZURE_SUBSCRIPTION_ID and AZURE_WEBAPP_NAME. These IDs are not secret credentials.
5. Push a change: CI runs offline tests. Actions → manual-learning-deployment → Run workflow
   runs tests, authenticates via OIDC, deploys the package and checks /health.
6. Intentionally break a test on a branch; verify CI stops deployment. Revert it. Keep prior
   validated packages/configuration so you can redeploy the previous release for rollback.

The sample CI does not invoke paid model judges. Add a protected live evaluation stage with
explicit budget, credentials and acceptance thresholds after lab 23. A green offline CI run
is not evidence of deployed model quality.
