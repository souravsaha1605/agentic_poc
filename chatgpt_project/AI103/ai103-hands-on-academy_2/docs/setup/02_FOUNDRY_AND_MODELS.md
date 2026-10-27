# Microsoft Foundry project and model setup

Portal labels evolve. These steps target the new Foundry experience and Projects SDK 2.x,
not classic hub/projects SDK 1.x. Keep the endpoint type and SDK generation together.

1. Open Azure Portal, create or select a Microsoft Foundry resource in the learning resource
   group, then open the Foundry portal. Create a project such as `ai103-learning`.
2. In the model catalog choose a chat model supporting chat completions. Deploy it under a
   name you choose, e.g. `lab-small`. Record region, deployment type, model/version and quota.
   A name here is your deployment name, not necessarily the catalog model name.
3. Deploy a second compatible model for comparisons (`lab-reasoning`). You may initially point
   both variables to one deployment to test plumbing, but that is not a model comparison.
   Add an embedding deployment for lab 08 and a vision-capable deployment for lab 24 only when
   needed. Check structured-output/tool-call support before labs 03/12.
4. From the inference resource/deployment page record the **resource endpoint** root, e.g.
   `https://<resource>.openai.azure.com`, and a key for the introductory key-based examples.
   Set AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY and MODEL_SMALL/MODEL_REASONING. Do not
   include `/chat/completions` in the endpoint; the adapter adds `/openai/v1/`.
5. Store values in your Databricks secret scope (recommended path) or local `.env`. In the model
   playground send a harmless prompt first. Then run lab 02 live; the two paths should reach the
   same deployments. Keep token usage and latency as evidence.
6. For keyless model calls, set MODEL_AUTH=entra and configure an identity with the appropriate
   Azure OpenAI data-plane role, such as Cognitive Services OpenAI User on that resource.
   The example token provider uses the documented https://ai.azure.com/.default scope for this v1 inference endpoint.
7. For lab 16, copy the separate **project endpoint** from the project overview:
   `https://<resource>.services.ai.azure.com/api/projects/<project>`. Set FOUNDRY_PROJECT_ENDPOINT.
   Give the actual notebook/service principal the project role needed to create and use agents.
   Current documentation calls the role Foundry User; some interfaces still show Azure AI User.
   Creation/admin permissions differ from agent-only consumption permissions.
8. Install `requirements/agents.txt`, run lab 16, then inspect the created agent version. Delete
   the learning agent/version manually after the exercise if no longer needed. The script deletes
   its conversation, but intentionally retains the agent for inspection.

For the managed-agent tool extension, open the agent editor, add a permitted knowledge/search
connection or custom tool, attach only the learning index/API, and test one query. Inspect the
service/tool identity and trace. Local Python functions are not automatically deployed as managed
agent tools; use the supported function/OpenAPI/MCP mechanism shown by your portal/SDK version.

Deployment options trade capacity, regional availability, data-processing geography and cost.
Do not equate global/data-zone/regional deployment labels with a promise of private networking.
Record the option selected and justify it against data-location and throughput requirements.

References:
- https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/prompt-agent
- https://learn.microsoft.com/en-us/azure/foundry/openai/api-version-lifecycle
- https://learn.microsoft.com/azure/ai-foundry/concepts/rbac-ai-foundry
