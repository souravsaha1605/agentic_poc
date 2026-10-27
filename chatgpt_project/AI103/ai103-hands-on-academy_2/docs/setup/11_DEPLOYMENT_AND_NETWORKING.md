# Deploy and operate the learning application

Databricks is the learning execution environment. This optional section deploys a small
synthetic-policy API to Azure App Service to practice application operations.

## Infrastructure and identity

Read `infra/README.md`. The Bicep template creates a Linux App Service plan/app with system
managed identity, a Key Vault, Log Analytics and Application Insights. It does not provision
all optional AI services, model quota or private networking. These are configured incrementally
in their respective portal guides. Run Bicep build and what-if before a resource-group deployment.
Use a dedicated group and inspect costs; the App Service plan incurs charges while provisioned.

In the deployed web app's **Identity**, verify the managed identity. Assign it only the required
model/data roles. In **Environment variables / Configuration**, add endpoint/deployment names,
MODEL_AUTH=entra, API_LIVE=true only after the local API works, and API_DEMO_TOKEN from a Key Vault
reference or secure setting. The synthetic API uses a shared demo token, not a full multi-user
identity implementation; do not expose real customer tools through it.

Use the code packaging script and App Service deployment commands in infra/README.md. Start
with API_LIVE=false to smoke-test routing without paid calls. Verify /health then an authenticated
/ask. Check telemetry. Reject unauthenticated requests. Record deployment artifact version and
roll back to the previous package when a smoke/evaluation gate fails.

## Private networking exercise

For each service identify the inbound client and outbound dependency. Create an approved VNet
and dedicated subnet(s); use separate subnet roles where required. Enable App Service VNet
integration for outbound access. On a target service create a private endpoint, approve the
connection, and link the required private DNS zone to the client VNet. Resolve the service FQDN
from the actual client environment and verify it resolves/reaches the private endpoint.
Then restrict public access and retest. Do not disable public access before your private route
and DNS are working.

Databricks has its own workspace/compute networking configuration. The App Service VNet path
does not grant Databricks access. Work with the workspace network owner on approved VNet
injection/private connectivity and outbound rules. Test from the Databricks driver itself.
Document which endpoint, DNS zone and identity each service requires. Never replace a missing
network path by granting broad public access to organizational data.

## CI CD and Foundry project lifecycle

The supplied CI runs local behavioral tests, all offline labs and the deterministic evaluation
gate. `deploy.yml` is manual and uses Azure workload federation/OIDC; configure repository
variables and the Azure federated credential first. It uploads code, not .env or source documents.
The workflow includes a health smoke check and fails on HTTP errors. Add live
quality gates in a protected environment with bounded budgets before promotion.

Version prompt text, tool schemas, retrieval/index schema and model configuration. To automate
managed agent updates, call the versioned agent creation code from lab 16 as an explicit release
step with project-scoped identity permissions; record the returned version. Do not treat an
application code deployment as proof that the Foundry agent definition was updated.

References:
- https://learn.microsoft.com/en-us/azure/app-service/configure-language-python
- https://learn.microsoft.com/en-us/azure/app-service/quickstart-python
