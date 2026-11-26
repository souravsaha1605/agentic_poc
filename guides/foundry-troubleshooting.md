# Microsoft Foundry troubleshooting

Use the exact error code, request ID, UTC timestamp, endpoint type, deployment name, identity, and request stage to narrow down a failure. Remove tokens, keys, customer content, and sensitive trace fields from shared diagnostics. Page numbers refer to the supplied documentation.

| Symptom | Checks and resolution | Verify | Source pages |
| --- | --- | --- | --- |
| HTTP 400 | Compare body fields, API surface, supported parameters, and model capabilities. Reduce the request to a supported baseline. For content filtering, inspect the returned safety code and handle it explicitly. | A supported minimal request returns a result. | 2109–2112 |
| HTTP 401 | Check credential type, token expiry and audience, and service endpoint. Sign in again for local Entra authentication if needed. | The same minimal authenticated request succeeds. | 2109–2112 |
| HTTP 403 | Read the response body. Check RBAC scope, disabled local authentication, and network restrictions independently. If using a private endpoint, check DNS from the caller's network. | The authorized principal can call from the expected network. | 2109–2112, 4261–4266 |
| HTTP 404 | Verify resource, region, endpoint type, deployment name and API route. For published agents, use the application endpoint specified for the protocol. | The exact deployment or application responds to a documented test input. | 2109–2112, 4256–4266 |
| HTTP 429 | Compare request and token consumption with the deployment limits, read the retry delay header, and use bounded backoff. Check whether a provisioned deployment is saturated. | Error rate drops under comparable traffic and replayed work remains bounded. | 1905, 2060, 2109–2112 |
| HTTP 500 or 503 | Retry transient errors with bounded exponential backoff. Record request IDs and inspect Azure service health if persistent. | A representative request works and the error rate recovers. | 2109–2112 |
| Model deployment fails | Check model/version regional support, SKU, subscription quota and capacity. Validate that the target region and deployment type match the request. | Deployment finishes and a short inference call succeeds. | 1891, 2033, 2104–2108 |
| Model router fails or selects unexpectedly | Check supported model options, router deployment configuration and routing mode. Inspect returned model information for representative prompts. | The router responds and returned routing metadata matches the expected policy. | 1708, 1837 |
| Hosted agent fails to start | Check CLI extension and runtime versions, project directory, service manifest, dependency sync and startup logs. Verify required project/model settings. | The local invocation returns an answer before a hosted rollout. | 3517, 3574, 3701 |
| Toolbox discovery or authorization fails | Confirm the deployed toolbox endpoint and connection authentication mode. For Language MCP, check the project identity and its Language role. | A minimal tool-list or read-only tool request succeeds under the intended identity. | 3523–3529, 4310, 4910 |
| Published agent fails under a user's identity | Confirm publish status, correct application endpoint, token audience and appropriate assignment for the calling identity. | Invoke as the intended signed-in user. | 4256–4266 |
| Private retrieval or hosted networking fails | Check inbound and outbound paths independently. Inspect private endpoint approval, DNS, and required service access from the actual caller network. | Resolve the expected private IP and complete the documented retrieval validation. | 4556–4588, 6689–6697 |
| Traces missing | Check project linkage to Application Insights, telemetry export and trace access. For external agents, verify registration and matching agent ID. Allow for ingestion delay. | A new invocation appears in the expected project and agent trace view. | 5011, 5069–5078, 5103, 5923 |
| Evaluation job fails or scores look wrong | Validate dataset fields against evaluator inputs and check project permissions and judge deployment. Inspect row-level results before relying on aggregate scores. | A small known dataset produces the expected row outputs and metrics. | 5296, 5303, 5318, 5389 |
| Browser Automation tool fails | Check the connected browser resource and its session, access and network configuration. Reproduce with a small approved task. | The same allowed test page opens and its expected content is returned. | 4683, 4698 |
| Programmed Training stalls or fails | Check the run status and logs, input dataset, supported configuration and available compute before relaunching. | A small valid training job advances beyond the failing stage. | 2874 |

For detailed source locations, see the [source index](source-index.md). The verification column translates the documented remedies into practical recovery checks.

## Evaluation, storage, and telemetry checks

The source troubleshooting article distinguishes the evaluation service, the judge deployment, and the storage connection. Check them in that order when the failure identifies an evaluation stage. [PDF pp. 5103–5111](source-index.md#observability)

1. **Dataset download or result upload fails.** Verify that the project has an Azure Blob Storage connection and determine its authentication mode.
2. **Storage returns `AuthorizationPermissionMismatch`.** For Entra authentication, verify that the project's managed identity has **Storage Blob Data Contributor** at the storage account scope. Allow the documented propagation interval before retrying.
3. **Storage requests time out.** Check the storage account's network configuration and the evaluation path. Verify network access and permission independently.
4. **No score appears for a row.** Look at the per-row failure details. Check that each evaluator's required fields are present and mapped, and that the judge deployment has quota and supports the operation.
5. **The trace appears in Application Insights but is absent in Foundry.** For an external agent, compare the registered identifier with the exported `gen_ai.agent.id` attribute and check the project and access scope. Generate a fresh trace and allow for ingestion.
