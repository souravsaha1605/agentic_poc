# Microsoft Foundry project catalog

The 14 packaged projects below follow Microsoft Learn’s Foundry navigation. Start with the two credential-free exercises or follow Get started from top to bottom. Each folder includes the source, file guide, original execution sequence, manual steps, and an automated entry point. The source notes identify adaptations and pinned upstream code.

The [walkthrough inventory](source-walkthroughs.md) links further quickstarts, tutorials, and samples. The [official topic index](../guides/source-index.md) covers the full Learn navigation and maps related articles to these projects.

## Get started

| Project | Problem and approach | Foundry services | PDF pages |
| --- | --- | --- | --- |
| [Enterprise workplace assistant](enterprise-workplace-assistant/README.md) | Answer employee questions using company policies and external technical guidance. Run batch evaluation against example questions. | Foundry Agent Service, Foundry Models, SharePoint connection, Microsoft Learn MCP, Foundry Evaluation | 30 |
| [Prompt agent and conversation](prompt-agent/README.md) | Create a managed prompt agent and show context across two turns. | Foundry Agent Service, Foundry Models, Responses API, Application Insights | 3056 |
| [Ephemeral Responses agent](ephemeral-responses-agent/README.md) | Keep the model and instructions in application code and invoke without creating an agent version. | Foundry Models, Foundry project Responses API | 3066 |
| [Bring your own hosted agent](custom-hosted-agent/README.md) | Wrap application code in the Foundry Responses hosting library. | Foundry Agent Service, Foundry Models, Responses API | 3574 |

## Models

| Project | Problem and approach | Foundry services | PDF pages |
| --- | --- | --- | --- |
| [Model router](model-router/README.md) | Send requests to one deployment that routes to a supported underlying model. | Foundry Models, model router, Responses API | 1708 |
| [Extract events with structured outputs](structured-outputs/README.md) | Define an event schema, constrain the response and validate its data. | Foundry Models, Responses API | 2406 |
| [Embedding document search](embedding-document-search/README.md) | Embed summaries and a query, then rank documents by cosine similarity. | Foundry Models, Azure OpenAI embeddings | 2531 |

## Agents

| Project | Problem and approach | Foundry services | PDF pages |
| --- | --- | --- | --- |
| [First hosted agent](hosted-agent/README.md) | Package a Python Agent Framework agent, start the Responses host, and invoke it. | Foundry Agent Service, Foundry Models, Microsoft Agent Framework | 3517 |

## Toolboxes

| Project | Problem and approach | Foundry services | PDF pages |
| --- | --- | --- | --- |
| [Hosted agent with a toolbox](hosted-agent-toolbox/README.md) | Expose tools through a single MCP endpoint and connect the hosted agent to that toolbox. | Foundry Agent Service, Foundry Toolboxes, Foundry MCP, Azure Language MCP, GitHub MCP | 3523 |
| [Ground answers with File Search](file-search/README.md) | Index product information, then stream answers and inspect citations. | Foundry Agent Service, File Search, vector stores, Responses API | 4626 |

## Observability

| Project | Problem and approach | Foundry services | PDF pages |
| --- | --- | --- | --- |
| [Convert traces into an evaluation dataset](trace-to-evaluation-dataset/README.md) | Turn recent agent interactions into a reusable evaluation dataset. | Foundry Agent Service, Foundry Models, Application Insights, Foundry Datasets | 5079 |

## Evaluation

| Project | Problem and approach | Foundry services | PDF pages |
| --- | --- | --- | --- |
| [Evaluate agent responses](agent-response-evaluation/README.md) | Evaluate an agent response against criteria using inline query inputs. | Foundry Agent Service, Foundry Models, Foundry Evaluation | 5325 |
| [Simulate and evaluate agent conversations](conversation-simulation/README.md) | Use scenario seeds to drive multi-turn conversations and evaluate the resulting behavior. | Foundry Agent Service, Foundry Models, Foundry Evaluation | 5372 |

## Optimization

| Project | Problem and approach | Foundry services | PDF pages |
| --- | --- | --- | --- |
| [Optimize a customer support agent](customer-support-optimization/README.md) | Use representative customer queries and evaluation criteria to compare instruction candidates. | Foundry Agent Service, Foundry Models, Agent Optimizer, Foundry Evaluation | 3557 |

## Run status

- [Embedding document search](embedding-document-search/README.md) ran offline and ranked the clean-energy bill first using illustrative vectors.
- [Structured outputs](structured-outputs/README.md) ran offline and validated a science-fair event against the JSON Schema.
- Live runners require the Azure resources listed in their project guides. The hosted-agent runners invoke a local host with a real Foundry deployment. The optimization runner serves the baseline support agent; the source sequence covers the separate optimization job.

[Terminology and examples](../guides/foundry-terminology.md) · [Troubleshooting](../guides/foundry-troubleshooting.md)
