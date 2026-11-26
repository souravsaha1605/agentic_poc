# Microsoft Foundry terminology

Use the alphabetical index below to jump to a term. Page numbers refer to the original PDF. The [official Learn topic index](source-index.md) follows Microsoft’s navigation and lists every article in the current table of contents. This glossary explains selected terms used across those sections. Examples are condensed practice scenarios based on the cited sections.

**Very important** marks a concept routinely needed in production Foundry development or operations. **Important** marks a concept widely used in a specific workflow or role. These editorial ratings reflect practical use and are independent of feature maturity.

## Alphabetical index

| Term | Industry relevance |
| --- | --- |
| [Agent application](#agent-application) | Important |
| [Agent identity](#agent-identity) | Very important |
| [Agent optimizer](#agent-optimizer) | Important |
| [Agent version](#agent-version) | Very important |
| [Agent-to-Agent (A2A)](#agent-to-agent-a2a) | Important |
| [AI gateway](#ai-gateway) | Very important |
| [Application Insights](#application-insights) | Very important |
| [Application lifecycle](#application-lifecycle) | Very important |
| [Azure Blob Storage connection](#azure-blob-storage-connection) | Very important |
| [Azure Cost Management](#azure-cost-management) | Very important |
| [Azure Developer CLI (azd)](#azure-developer-cli-azd) | Important |
| [Azure OpenAI](#azure-openai) | Very important |
| [Azure Policy](#azure-policy) | Very important |
| [Batch processing](#batch-processing) | Important |
| [Bring your own storage](#bring-your-own-storage) | Important |
| [Browser Automation](#browser-automation) | Important |
| [Capacity and quota](#capacity-and-quota) | Very important |
| [Chat Completions API](#chat-completions-api) | Very important |
| [Chunking](#chunking) | Very important |
| [Code Interpreter](#code-interpreter) | Important |
| [Connection](#connection) | Very important |
| [Content filtering](#content-filtering) | Very important |
| [Conversation](#conversation) | Very important |
| [Cosine similarity](#cosine-similarity) | Important |
| [Cost controls](#cost-controls) | Very important |
| [Cross-region disaster recovery](#cross-region-disaster-recovery) | Important |
| [Data plane](#data-plane) | Very important |
| [Data zone deployment](#data-zone-deployment) | Important |
| [DefaultAzureCredential](#defaultazurecredential) | Very important |
| [Deployment type](#deployment-type) | Very important |
| [Embedding](#embedding) | Very important |
| [Endpoint](#endpoint) | Very important |
| [Ephemeral agent](#ephemeral-agent) | Important |
| [Evaluation dataset](#evaluation-dataset) | Very important |
| [Evaluation run](#evaluation-run) | Very important |
| [Evaluator](#evaluator) | Very important |
| [File Search](#file-search) | Important |
| [Flex processing](#flex-processing) | Important |
| [Foundry (classic)](#foundry-classic) | Important |
| [Foundry Agent Service](#foundry-agent-service) | Very important |
| [Foundry IQ](#foundry-iq) | Important |
| [Foundry Models](#foundry-models) | Very important |
| [Foundry project](#foundry-project) | Very important |
| [Foundry Toolkit](#foundry-toolkit) | Important |
| [Function calling](#function-calling) | Very important |
| [Global Standard](#global-standard) | Important |
| [Groundedness](#groundedness) | Very important |
| [Guardrail](#guardrail) | Very important |
| [Hosted agent](#hosted-agent) | Very important |
| [Human feedback](#human-feedback) | Important |
| [Inference](#inference) | Very important |
| [JSON mode](#json-mode) | Important |
| [LoRA adapter](#lora-adapter) | Important |
| [Managed identity](#managed-identity) | Very important |
| [Managed virtual network](#managed-virtual-network) | Very important |
| [Management plane](#management-plane) | Very important |
| [Microsoft Entra ID](#microsoft-entra-id) | Very important |
| [Model Context Protocol (MCP)](#model-context-protocol-mcp) | Very important |
| [Model deployment](#model-deployment) | Very important |
| [Model lifecycle](#model-lifecycle) | Very important |
| [Model retirement](#model-retirement) | Very important |
| [Model router](#model-router) | Important |
| [Network injection](#network-injection) | Important |
| [OpenAPI tool](#openapi-tool) | Important |
| [OpenTelemetry](#opentelemetry) | Very important |
| [Persistent memory](#persistent-memory) | Important |
| [Priority processing](#priority-processing) | Important |
| [Private DNS](#private-dns) | Very important |
| [Private endpoint](#private-endpoint) | Very important |
| [Prompt agent](#prompt-agent) | Very important |
| [Prompt Shields](#prompt-shields) | Important |
| [Provisioned spillover](#provisioned-spillover) | Important |
| [Provisioned throughput units (PTU)](#provisioned-throughput-units-ptu) | Important |
| [Responses API](#responses-api) | Very important |
| [Retrieval-augmented generation (RAG)](#retrieval-augmented-generation-rag) | Very important |
| [Role-based access control (RBAC)](#role-based-access-control-rbac) | Very important |
| [Routines](#routines) | Important |
| [RPM and TPM](#rpm-and-tpm) | Very important |
| [Service health](#service-health) | Very important |
| [Span and trace](#span-and-trace) | Very important |
| [Structured outputs](#structured-outputs) | Very important |
| [Synthetic evaluation data](#synthetic-evaluation-data) | Important |
| [Task adherence](#task-adherence) | Important |
| [Token usage](#token-usage) | Very important |
| [Tool search](#tool-search) | Important |
| [Toolbox](#toolbox) | Important |
| [Trace-based evaluation](#trace-based-evaluation) | Important |
| [Vector store](#vector-store) | Very important |
| [Voice Live](#voice-live) | Important |

## Agent application

**Industry relevance** · Important

A publishable application surface for an agent, with its own invocation and access settings.

**Example** · Publish an internal assistant so a supported client can invoke it.

**Source pages** · [3108](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/agent-applications)

## Agent identity

**Industry relevance** · Very important

The identity an agent uses when calling protected resources. The target resource separately grants permissions.

**Example** · Grant the agent read access to its knowledge source.

**Source pages** · [4910](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/tool-authentication), [4261](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/troubleshoot-publish-copilot-authorization)

## Agent optimizer

**Industry relevance** · Important

A workflow that proposes changes to an agent and scores candidates against evaluations.

**Example** · Compare changed support instructions to a baseline and verify the selected version on an independent dataset.

**Source pages** · [3557](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/quickstart-optimize-hosted-agent), [5597](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/quickstart-optimize-hosted-agent)

## Agent version

**Industry relevance** · Very important

A revision of an agent definition that can be invoked or promoted independently.

**Example** · Create a new prompt agent version when changing its instructions.

**Source pages** · [3056](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/prompt-agent), [3991](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/deploy-hosted-agent-production)

## Agent-to-Agent (A2A)

**Industry relevance** · Important

A protocol-facing tool option for sending a task to a remote agent.

**Example** · Connect a specialist agent from a toolbox and invoke it using its remote endpoint.

**Source pages** · [4310](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/toolbox)

## AI gateway

**Industry relevance** · Very important

An Azure API Management gateway can apply policies to model requests or MCP tool traffic and provide a governed access point.

**Example** · Enforce a token limit at the gateway for a model endpoint.

**Source pages** · [6514](https://learn.microsoft.com/en-us/azure/foundry/configuration/enable-ai-api-management-gateway-portal), [6523](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/governance), [6529](https://learn.microsoft.com/en-us/azure/foundry/control-plane/how-to-enforce-limits-models)

## Application Insights

**Industry relevance** · Very important

Azure Monitor's application telemetry destination for traces and metrics.

**Example** · Send a test invocation and find its trace in the Foundry portal.

**Source pages** · [5011](https://learn.microsoft.com/en-us/azure/foundry/observability/quickstarts/quickstart-tracing-hosted-agent), [5103](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/troubleshooting), 5923

## Application lifecycle

**Industry relevance** · Very important

The process of promoting and rolling out versions of a hosted agent across environments.

**Example** · Test a new agent version before routing production traffic to it.

**Source pages** · [3991](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/deploy-hosted-agent-production)

## Azure Blob Storage connection

**Industry relevance** · Very important

A connection that lets supported Foundry workflows read datasets and write results in Azure Storage.

**Example** · Link Blob Storage and grant the project identity the documented data role for evaluation.

**Source pages** · [5103](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/troubleshooting), [6728](https://learn.microsoft.com/en-us/azure/foundry/how-to/connections-add)

## Azure Cost Management

**Industry relevance** · Very important

Azure tooling for analyzing billed usage and spending at supported scopes.

**Example** · Filter resource spending by scope and compare it with Foundry usage views.

**Source pages** · [5729](https://learn.microsoft.com/en-us/azure/foundry/how-to/analyze-costs-cost-management)

## Azure Developer CLI (azd)

**Industry relevance** · Important

CLI used in hosted-agent walkthroughs to initialize, provision, run, deploy, and invoke agents.

**Example** · Run azd ai agent invoke --local after starting the agent.

**Source pages** · [3517](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/quickstart-hosted-agent), [3574](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/quickstart-deploy-own-code)

## Azure OpenAI

**Industry relevance** · Very important

OpenAI models exposed through Azure endpoints with Azure deployments and access controls.

**Example** · Call an Azure deployment using its deployment name through Responses.

**Source pages** · [2109](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/troubleshoot-errors), [2352](https://learn.microsoft.com/azure/developer/ai/how-to/azure-openai-to-responses?context=/azure/foundry/context/context)

## Azure Policy

**Industry relevance** · Very important

Azure governance that evaluates deployments against policy definitions at an assigned scope.

**Example** · Audit diagnostic settings across Foundry resources.

**Source pages** · [5802](https://learn.microsoft.com/en-us/azure/ai-services/policy-reference?context=/azure/foundry/context/context), [5806](https://learn.microsoft.com/en-us/azure/foundry/how-to/model-deployment-policy), [5825](https://learn.microsoft.com/en-us/azure/foundry/how-to/custom-policy-definition)

## Batch processing

**Industry relevance** · Important

Submit a file of requests as an asynchronous processing job.

**Example** · Queue classification for a large set of records and download the eventual results.

**Source pages** · [1991](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/batch)

## Bring your own storage

**Industry relevance** · Important

Use a customer-managed storage resource in supported Foundry configurations.

**Example** · Connect storage governed by your organization’s network and access policies.

**Source pages** · [6660](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/use-your-own-resources)

## Browser Automation

**Industry relevance** · Important

A Foundry tool that lets an agent interact with a browser through a connected tool endpoint.

**Example** · Practice a navigation task against an approved test website.

**Source pages** · [3537](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/browser-automation-hosted-agent-quickstart), [4698](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/browser-automation-manage-troubleshoot)

## Capacity and quota

**Industry relevance** · Very important

Quota limits the amount of deployment capacity you can assign. Regional capacity also affects whether Azure can fulfill a deployment.

**Example** · Check subscription quota and regional model availability if a deployment fails.

**Source pages** · [1891](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/automate-quota-deployments), [2033](https://learn.microsoft.com/en-us/azure/foundry/openai/provisioned-quickstart), [2104](https://learn.microsoft.com/en-us/azure/foundry-classic/how-to/troubleshoot-deploy-and-monitor?context=/azure/foundry/context/context)

## Chat Completions API

**Industry relevance** · Very important

Azure OpenAI interface that accepts message history and returns a completion.

**Example** · Pass system and user messages while maintaining history in the application.

**Source pages** · [2352](https://learn.microsoft.com/azure/developer/ai/how-to/azure-openai-to-responses?context=/azure/foundry/context/context)

## Chunking

**Industry relevance** · Very important

Splitting source documents into smaller units so retrieval can return relevant passages.

**Example** · Store sections of a policy so a question retrieves the relevant clause.

**Source pages** · [4547](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/foundry-iq-connect), [4626](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/file-search)

## Code Interpreter

**Industry relevance** · Important

A managed agent tool for executing code in a sandbox to analyze supplied data or generate files.

**Example** · Ask an agent to summarize a CSV and create a chart.

**Source pages** · [4300](https://learn.microsoft.com/en-us/azure/foundry/agents/faq), [4310](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/toolbox)

## Connection

**Industry relevance** · Very important

A project or toolbox configuration that connects a service or tool with its authentication settings.

**Example** · Configure an Azure Language MCP connection that uses the project identity.

**Source pages** · [4310](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/toolbox), [4910](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/tool-authentication), [6728](https://learn.microsoft.com/en-us/azure/foundry/how-to/connections-add)

## Content filtering

**Industry relevance** · Very important

A safety policy that checks model inputs or outputs for configured risk categories.

**Example** · Handle a filtered prompt separately from a transport or authentication failure.

**Source pages** · [2109](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/troubleshoot-errors), [6073](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/content-filter-prompt-shields)

## Conversation

**Industry relevance** · Very important

Stored context that can be reused across Responses calls.

**Example** · Ask about France, then ask for its capital with the same conversation ID.

**Source pages** · [3056](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/prompt-agent), [3066](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/responses-api)

## Cosine similarity

**Industry relevance** · Important

A measure of how closely two vector directions align, used to rank embeddings.

**Example** · Compare a query embedding with embedded BillSum summaries.

**Source pages** · [2531](https://learn.microsoft.com/en-us/azure/foundry/openai/tutorials/embeddings)

## Cost controls

**Industry relevance** · Very important

Foundry controls for managing usage and spend, scoped to supported resources and actions.

**Example** · Configure a spending threshold and review the action it applies.

**Source pages** · [5741](https://learn.microsoft.com/en-us/azure/foundry/concepts/cost-controls), [5751](https://learn.microsoft.com/en-us/azure/foundry/how-to/create-cost-controls)

## Cross-region disaster recovery

**Industry relevance** · Important

Recovery planning for service outage or resource loss, including the resources and data needed in a second region.

**Example** · Prepare the dependencies needed to restore an agent in a secondary region.

**Source pages** · [5982](https://learn.microsoft.com/en-us/azure/foundry/how-to/agent-service-disaster-recovery), [5987](https://learn.microsoft.com/en-us/azure/foundry/how-to/agent-service-platform-disaster-recovery), [5997](https://learn.microsoft.com/en-us/azure/foundry/how-to/agent-service-operator-disaster-recovery)

## Data plane

**Industry relevance** · Very important

The endpoint and operations used to invoke deployed capabilities or work with service data.

**Example** · Send an inference request to the Responses endpoint.

**Source pages** · [610](https://learn.microsoft.com/en-us/azure/foundry/openai/api-version-lifecycle), [2109](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/troubleshoot-errors)

## Data zone deployment

**Industry relevance** · Important

A model deployment type that constrains processing to a designated data zone.

**Example** · Choose a supported data zone when processing geography is a requirement.

**Source pages** · [1925](https://learn.microsoft.com/en-us/azure/foundry/concepts/deployments-overview), [2033](https://learn.microsoft.com/en-us/azure/foundry/openai/provisioned-quickstart)

## DefaultAzureCredential

**Industry relevance** · Very important

An Azure Identity credential chain that can use configured local and hosted identities.

**Example** · Use az login locally and an assigned managed identity in Azure.

**Source pages** · [3056](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/prompt-agent)

## Deployment type

**Industry relevance** · Very important

A serving option that controls processing geography, performance and pricing characteristics.

**Example** · Compare Standard and provisioned deployment options for a traffic pattern.

**Source pages** · [1925](https://learn.microsoft.com/en-us/azure/foundry/concepts/deployments-overview), [1975](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/deployment-types)

## Embedding

**Industry relevance** · Very important

A numeric vector representation used to compare semantic similarity.

**Example** · Embed a search query and document texts using the same embedding model.

**Source pages** · [2531](https://learn.microsoft.com/en-us/azure/foundry/openai/tutorials/embeddings)

## Endpoint

**Industry relevance** · Very important

The service URL targeted by the client. Foundry project, Azure OpenAI and published agent endpoints have different purposes.

**Example** · Use the URL containing /api/projects/ for AIProjectClient.

**Source pages** · [3056](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/prompt-agent), [3066](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/responses-api), [2109](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/troubleshoot-errors)

## Ephemeral agent

**Industry relevance** · Important

An agent whose model, instructions, and tools are defined in application code and supplied at invocation.

**Example** · Construct a Responses invocation with an application-defined instruction.

**Source pages** · [3066](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/responses-api)

## Evaluation dataset

**Industry relevance** · Very important

A collection of structured inputs and optional reference outputs or traces used to measure behavior.

**Example** · Use JSONL support questions to score a hosted agent before release.

**Source pages** · [5296](https://learn.microsoft.com/en-us/azure/foundry/observability/quickstarts/quickstart-evaluate-hosted-agent), [5318](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-datasets), [5352](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-conversations)

## Evaluation run

**Industry relevance** · Very important

An execution of the evaluation configuration against a specific dataset or target.

**Example** · Inspect row results after the run reaches a completed state.

**Source pages** · [5296](https://learn.microsoft.com/en-us/azure/foundry/observability/quickstarts/quickstart-evaluate-hosted-agent), [5389](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-results)

## Evaluator

**Industry relevance** · Very important

A model-assisted or code-based grader that measures a specific output property.

**Example** · Score the groundedness of an answer against retrieved evidence.

**Source pages** · [5136](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/general-purpose-evaluators), [5146](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators), [5165](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/agent-evaluators)

## File Search

**Industry relevance** · Important

A managed retrieval tool that searches files associated with a vector store.

**Example** · Upload a document and ask the agent to find a relevant section.

**Source pages** · [4626](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/file-search)

## Flex processing

**Industry relevance** · Important

An inference tier for workloads that can tolerate greater latency and availability variability.

**Example** · Run a nonurgent offline inference task on a supported deployment.

**Source pages** · [2002](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/flex-processing)

## Foundry (classic)

**Industry relevance** · Important

The legacy portal experience where hub-based projects remain accessible.

**Example** · Open a hub-based project in the classic portal when reviewing a migration.

**Source pages** · [100](https://learn.microsoft.com/en-us/azure/foundry/how-to/navigate-from-classic)

## Foundry Agent Service

**Industry relevance** · Very important

The managed service for building, invoking, and operating agents in a Foundry project.

**Example** · Use it to version a prompt agent or deploy a code-based agent.

**Source pages** · [3056](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/prompt-agent), [3517](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/quickstart-hosted-agent)

## Foundry IQ

**Industry relevance** · Important

A knowledge retrieval capability that connects agents to knowledge bases and returns grounding information.

**Example** · Connect a knowledge base to answer a question using indexed internal material.

**Source pages** · [4539](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/what-is-foundry-iq), [4547](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/foundry-iq-connect), [4556](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/foundry-iq-tutorial-private-overview)

## Foundry Models

**Industry relevance** · Very important

The model catalog and deployment capabilities that supply inference to applications and agents.

**Example** · Deploy an embedding model and reference its deployment name.

**Source pages** · 1905, [2033](https://learn.microsoft.com/en-us/azure/foundry/openai/provisioned-quickstart), [2531](https://learn.microsoft.com/en-us/azure/foundry/openai/tutorials/embeddings)

## Foundry project

**Industry relevance** · Very important

A development and management scope for Foundry assets such as agents, model access, connections and observability.

**Example** · Copy the project endpoint to build an SDK client for that project.

**Source pages** · [1](https://learn.microsoft.com/en-us/azure/foundry/what-is-foundry), [20](https://learn.microsoft.com/en-us/azure/foundry/tutorials/quickstart-create-foundry-resources), [3056](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/prompt-agent)

## Foundry Toolkit

**Industry relevance** · Important

A Visual Studio Code extension for developing Foundry resources and agents within the editor.

**Example** · Set the active Foundry project before opening the hosted-agent tooling.

**Source pages** · [146](https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/get-started-projects-visual-studio-code), [151](https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/install-foundry-toolkit-visual-studio-code)

## Function calling

**Industry relevance** · Very important

A model can request a tool call with structured arguments. Application-owned functions execute in application code.

**Example** · Have an agent request an order lookup and return the lookup result to it.

**Source pages** · [3066](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/responses-api), [4439](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/openapi)

## Global Standard

**Industry relevance** · Important

A standard model deployment option that permits global processing subject to Azure's documented rules.

**Example** · Use it for a latency-tolerant workload without a narrower processing boundary.

**Source pages** · [1975](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/deployment-types)

## Groundedness

**Industry relevance** · Very important

The extent to which an answer is supported by its supplied context.

**Example** · Score a benefits answer against retrieved policy excerpts.

**Source pages** · [5146](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators)

## Guardrail

**Industry relevance** · Very important

A safety control evaluated at an intervention point in an agent or model workflow.

**Example** · Apply a configured input check before a request is sent onward.

**Source pages** · [6016](https://learn.microsoft.com/en-us/azure/foundry/guardrails/guardrails-overview), [6023](https://learn.microsoft.com/en-us/azure/foundry/guardrails/how-to-create-guardrails), [6111](https://learn.microsoft.com/en-us/azure/foundry/guardrails/intervention-points)

## Hosted agent

**Industry relevance** · Very important

Agent code packaged and run by Foundry Agent Service using a defined invocation protocol.

**Example** · Host a Python Responses-based agent with a Dockerfile and azd manifest.

**Source pages** · [3517](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/quickstart-hosted-agent), [3574](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/quickstart-deploy-own-code)

## Human feedback

**Industry relevance** · Important

A rating or annotation attached to a response or trace so people can assess behavior.

**Example** · Record a thumbs-down rating and inspect the associated trace during review.

**Source pages** · [4975](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/log-end-user-feedback), [5087](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/trace-annotations)

## Inference

**Industry relevance** · Very important

Running a deployed model on input to produce text, embeddings, or another output.

**Example** · Send a query to an embedding deployment and read the resulting vector.

**Source pages** · [2109](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/troubleshoot-errors), [3066](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/responses-api)

## JSON mode

**Industry relevance** · Important

An output setting intended to return valid JSON.

**Example** · Request a JSON object for a product categorization result.

**Source pages** · [2418](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/json-mode)

## LoRA adapter

**Industry relevance** · Important

A smaller set of trained weights that adapts a base model without replacing all its weights.

**Example** · Deploy an adapter tuned for a specialized task on compatible managed compute.

**Source pages** · [1948](https://learn.microsoft.com/en-us/azure/foundry/concepts/adapter-deployment-overview), [1953](https://learn.microsoft.com/en-us/azure/foundry/how-to/deploy-lora-managed-compute)

## Managed identity

**Industry relevance** · Very important

An Azure-managed identity with tokens and resource grants, avoiding an application-owned credential for supported resources.

**Example** · Grant a project's managed identity the required Language data permissions.

**Source pages** · [4910](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/tool-authentication), [6660](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/use-your-own-resources)

## Managed virtual network

**Industry relevance** · Very important

Network isolation and routing for supported Foundry workloads, configured with the platform’s networking options.

**Example** · Check the DNS and routes available to a hosted runtime before testing a private dependency.

**Source pages** · [6689](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/troubleshoot-hosted-agent-networking)

## Management plane

**Industry relevance** · Very important

The layer used to provision and configure Azure resources.

**Example** · Use a Bicep template to provision a resource and model deployment.

**Source pages** · [610](https://learn.microsoft.com/en-us/azure/foundry/openai/api-version-lifecycle), [1295](https://learn.microsoft.com/azure/templates/microsoft.cognitiveservices/accounts?pivots=deployment-language-bicep)

## Microsoft Entra ID

**Industry relevance** · Very important

Azure identity system used to issue tokens, authenticate principals and enforce assigned access.

**Example** · Sign in to Azure CLI before constructing the SDK client locally.

**Source pages** · [2109](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/troubleshoot-errors), [3056](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/prompt-agent), [4261](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/troubleshoot-publish-copilot-authorization)

## Model Context Protocol (MCP)

**Industry relevance** · Very important

A protocol that exposes discoverable tools through an endpoint with an authentication scheme.

**Example** · Connect a hosted agent to a toolbox MCP endpoint.

**Source pages** · [3523](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/quickstart-toolbox-agent), [4341](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/model-context-protocol)

## Model deployment

**Industry relevance** · Very important

A named serving configuration for a model. Clients pass the deployment name when invoking it.

**Example** · Point FOUNDRY_MODEL_NAME to the deployment rather than a guessed catalog identifier.

**Source pages** · [1708](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/model-router), [2104](https://learn.microsoft.com/en-us/azure/foundry-classic/how-to/troubleshoot-deploy-and-monitor?context=/azure/foundry/context/context), [3056](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/prompt-agent)

## Model lifecycle

**Industry relevance** · Very important

The Azure policy for model versions, updates, retirement and migration.

**Example** · Track a scheduled model retirement before rolling out a replacement deployment.

**Source pages** · [1651](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-retirements), [6808](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-retirements)

## Model retirement

**Industry relevance** · Very important

The end of availability or support for a model version under the documented lifecycle policy.

**Example** · Validate a replacement deployment before migrating production callers.

**Source pages** · [1651](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-retirements), [6808](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-retirements)

## Model router

**Industry relevance** · Important

A model deployment that selects a supported underlying model for a request.

**Example** · Submit requests through a router deployment and inspect the reported model.

**Source pages** · [1708](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/model-router), [1837](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/model-router-troubleshoot)

## Network injection

**Industry relevance** · Important

Attach hosted agent sessions to a configured virtual network so they can reach private dependencies.

**Example** · Check DNS and TLS connectivity from the agent's delegated network path.

**Source pages** · [6689](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/troubleshoot-hosted-agent-networking)

## OpenAPI tool

**Industry relevance** · Important

A tool that describes supported REST operations through an OpenAPI specification.

**Example** · Expose a weather lookup through its API schema.

**Source pages** · [4439](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/openapi)

## OpenTelemetry

**Industry relevance** · Very important

Instrumentation and telemetry conventions used to collect spans for agent applications.

**Example** · Instrument the client and export spans to Application Insights.

**Source pages** · [5011](https://learn.microsoft.com/en-us/azure/foundry/observability/quickstarts/quickstart-tracing-hosted-agent), [5053](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/trace-agent-framework), [5069](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/register-external-agent)

## Persistent memory

**Industry relevance** · Important

State that can survive turns and, with appropriate storage and scope, later sessions.

**Example** · Store a user preference and retrieve it in a later interaction.

**Source pages** · [3542](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/quickstart-memory-hosted-agent), [3822](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/use-hosted-agent-memory-snapshots), [4840](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/memory-usage)

## Priority processing

**Industry relevance** · Important

An inference service tier designed for workloads where request latency matters.

**Example** · Use a supported priority tier for a customer-facing interaction.

**Source pages** · [2014](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/priority-processing)

## Private DNS

**Industry relevance** · Very important

DNS configuration that resolves a service hostname to the intended private endpoint address.

**Example** · Resolve the normal Foundry hostname from the caller’s network and compare its address with the configured endpoint.

**Source pages** · [4559](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/foundry-iq-tutorial-private-inbound), [6689](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/troubleshoot-hosted-agent-networking)

## Private endpoint

**Industry relevance** · Very important

A private IP network entry point for an Azure service.

**Example** · Confirm that the resource name resolves to the private IP from the caller network.

**Source pages** · [2109](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/troubleshoot-errors), [4559](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/foundry-iq-tutorial-private-inbound), [6689](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/troubleshoot-hosted-agent-networking)

## Prompt agent

**Industry relevance** · Very important

A declarative agent version defined through a model, instructions and optional tools.

**Example** · Create a PromptAgentDefinition and ask two related questions.

**Source pages** · [3056](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/prompt-agent)

## Prompt Shields

**Industry relevance** · Important

Content Safety detection for prompt injection or indirect attacks in untrusted input.

**Example** · Check whether supplied document text is attempting to redirect the agent.

**Source pages** · [6073](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/content-filter-prompt-shields)

## Provisioned spillover

**Industry relevance** · Important

A routing option for excess load when a provisioned deployment is constrained.

**Example** · Route eligible excess requests to a configured standard deployment.

**Source pages** · [2068](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/spillover-traffic-management)

## Provisioned throughput units (PTU)

**Industry relevance** · Important

Units used to allocate capacity for provisioned model serving.

**Example** · Size a deployment from representative traffic and monitor utilization.

**Source pages** · [2033](https://learn.microsoft.com/en-us/azure/foundry/openai/provisioned-quickstart), [2060](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/provisioned-get-started)

## Responses API

**Industry relevance** · Very important

An API for model and agent responses with tool orchestration and conversational options.

**Example** · Invoke a prompt agent and reuse the conversation ID for a follow-up.

**Source pages** · [2352](https://learn.microsoft.com/azure/developer/ai/how-to/azure-openai-to-responses?context=/azure/foundry/context/context), [3066](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/responses-api)

## Retrieval-augmented generation (RAG)

**Industry relevance** · Very important

Retrieving relevant source content and supplying it to the model to ground the response.

**Example** · Retrieve policy sections before answering a workplace question.

**Source pages** · [2531](https://learn.microsoft.com/en-us/azure/foundry/openai/tutorials/embeddings), [4547](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/foundry-iq-connect), [5146](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators)

## Role-based access control (RBAC)

**Industry relevance** · Very important

Azure access decisions based on principal, assigned role and scope.

**Example** · Grant a developer access to the appropriate project scope and retry the same call.

**Source pages** · [1](https://learn.microsoft.com/en-us/azure/foundry/what-is-foundry), [2109](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/troubleshoot-errors), [4261](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/troubleshoot-publish-copilot-authorization)

## Routines

**Industry relevance** · Important

Reusable agent actions that can run through configured triggers or schedules.

**Example** · Schedule a recurring agent task in a development project.

**Source pages** · [3031](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/routines), [3174](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/use-routines)

## RPM and TPM

**Industry relevance** · Very important

Requests per minute and tokens per minute, limits that can throttle model requests.

**Example** · Use retry-after-ms and smooth bursts when a deployment returns HTTP 429.

**Source pages** · 1905, [2109](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/troubleshoot-errors)

## Service health

**Industry relevance** · Very important

Azure status information used to determine whether a persistent failure coincides with a service incident.

**Example** · Check regional incidents after repeated 503 responses and capture request IDs.

**Source pages** · [2109](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/troubleshoot-errors)

## Span and trace

**Industry relevance** · Very important

A trace groups related operations. A span records one operation in the trace.

**Example** · Inspect the model span and tool span for a single slow request.

**Source pages** · [5011](https://learn.microsoft.com/en-us/azure/foundry/observability/quickstarts/quickstart-tracing-hosted-agent), [5079](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/traces-to-dataset), [5103](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/troubleshooting)

## Structured outputs

**Industry relevance** · Very important

A way to constrain generated results to a supplied schema.

**Example** · Require a JSON object with a typed category and explanation.

**Source pages** · [2406](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/structured-outputs)

## Synthetic evaluation data

**Industry relevance** · Important

Generated inputs used to extend test coverage.

**Example** · Generate questions for cases missing from a starter evaluation set.

**Source pages** · [5276](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-dataset-synthetic), [5347](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-synthetic-data)

## Task adherence

**Industry relevance** · Important

An evaluator dimension that measures whether an agent follows the task it was given.

**Example** · Define a minimum task adherence pass rate before promoting a release.

**Source pages** · [5165](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/agent-evaluators), [5296](https://learn.microsoft.com/en-us/azure/foundry/observability/quickstarts/quickstart-evaluate-hosted-agent)

## Token usage

**Industry relevance** · Very important

The input and output token units used in quota, cost, and workload measurements.

**Example** · Compare token consumption across two agent versions before promoting one.

**Source pages** · [5647](https://learn.microsoft.com/en-us/azure/foundry/concepts/manage-costs), [5701](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-optimizer-costs), [5766](https://learn.microsoft.com/en-us/azure/foundry/control-plane/how-to-enforce-limits-models)

## Tool search

**Industry relevance** · Important

Tool discovery that selects a relevant subset from a larger collection.

**Example** · Search a toolbox for tools related to the current request.

**Source pages** · [4857](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/tool-search)

## Toolbox

**Industry relevance** · Important

A versioned collection of tools accessible through one MCP endpoint.

**Example** · Group Language and Foundry tools for a hosted agent.

**Source pages** · [3523](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/quickstart-toolbox-agent), [4310](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/toolbox)

## Trace-based evaluation

**Industry relevance** · Important

Apply evaluators to data recorded in executions, including agent context and tool activity where available.

**Example** · Evaluate whether a traced agent run used the expected tool.

**Source pages** · [5079](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/traces-to-dataset), [5334](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-deployed-interactions)

## Vector store

**Industry relevance** · Very important

A store that indexes representations of files or passages for retrieval.

**Example** · Attach an uploaded policy to a vector store and use File Search.

**Source pages** · [4626](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/file-search)

## Voice Live

**Industry relevance** · Important

A real-time voice interface that supports conversational audio and integration with agents.

**Example** · Connect microphone input and receive a spoken response.

**Source pages** · [3216](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/prompt-voice-agent), [4816](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/voice-live-agents-quickstart)
