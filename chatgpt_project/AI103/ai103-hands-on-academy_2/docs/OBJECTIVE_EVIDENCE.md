# Coverage by evidence, not by filename

Use this with the handbook chapter map in COVERAGE.md. Each topic group has an implemented
exercise or an explicitly service-hosted exercise. Complete the action and retain evidence.
A listed path does not mean its live Azure behavior has been verified in your subscription.

| Topic group | Hands-on path | Evidence to retain |
|---|---|---|
| Identity and credentials | 01 + Azure hosting | Secret version; role denial |
| Model selection and settings | 02; 03_generation_controls | Deployment comparison; usage |
| Prompts and structured output | 03; 06_domain_extraction | Valid schema; missing evidence |
| Safety and injection | 04–05; 24_visual_evidence | Allowed/blocked cases |
| Retrieval and indexing | 08–11; 26_multimodal_ingestion | Retrieval results; source positions |
| Tools and authorization | 12–13; 12_rest_transport | Denied tool; argument validation |
| Agent-driven retrieval | 17 azure-search | Tool event; tenant-scoped result |
| Managed agents | 16 + Foundry tool exercise below | Agent version; conversation; tool trace |
| Reliability and memory | 14–15; summary extension | Deduplicated effect; expiry/isolation |
| Orchestration and reflection | 18–19; group discussion | Bounded stages; failed branch |
| Approval workflows | 20 + azure_execution/logic_apps | Pending/rejected/approved run IDs |
| MCP | 21 live | Protocol discovery/invocation |
| Monitoring and quality | 22–23; 23_rag_regression | Trace; failed/passed cases |
| Visual generation/editing | 28–29 | Masked image; video ID/remix |
| Visual understanding | 24; visual-evidence extension | Captions; question answer; OCR screen |
| Visual policy | visual-evidence/VISUAL_POLICY.md | Symbol/brand review; labelled asset |
| Language and translation | 06–07; domain extraction | Redaction; topics; translated conditions |
| Speech interactions | 27; capstone 03 speech | Transcript; reply WAV; no-match test |
| Custom models/analyzers | 25 custom; 26; agentic analyzer | Model/analyzer ID; schema comparison |
| Multimedia analysis | 26 audio/video + ingestion extension | Segment evidence and indexed chunks |
| Enterprise data | 30; Cosmos extension; capstone 04 fabric | Query results; source freshness |
| Deployment and networking | 31; azure_execution | What-if; smoke test; denied route |
| Cost and drift | 32 + monitoring portal exercise | Cost estimate; baseline comparison |

## Managed-agent knowledge/tool exercise

After lab 16, open its created agent in Foundry. Add the supported Azure AI Search knowledge
connection scoped to your learning index. Configure the connection identity and grant it Search
Index Data Reader plus any embedding/model permissions required by the chosen connection.
Use a separate public-only learning index for this portal exercise: attaching an index does not
inherit the Python application's tenant filter. Do not connect a mixed-tenant index without a
supported tested scope/filter configuration.

Ask a policy question, inspect the knowledge/tool trace and citation, then remove access and
repeat to see the failure. For a custom API use the supported OpenAPI/MCP tool configuration,
attach only the read-only learning endpoint, and inspect the declared authentication. The local
function in lab 12 is not automatically a remotely hosted Foundry tool. Record which tool actually
ran, its identity, arguments and returned evidence. Tool editor controls can differ by project/API.

## Multimedia progression

Use lab 26 with CU_ANALYZER=prebuilt-imageSearch and product.png, then prebuilt-audioSearch
with the lab 27 WAV, then prebuilt-videoSearch with a short consented/generated clip. Set the
analyzer ID in config_json and file in input_file each time. Inspect output metadata instead of
assuming every analyzer emits the same fields. Run 26_multimodal_ingestion on a result containing
markdown/text; query the separate media index. Keep page/time references for grounded answers.

## Retired features and production depth

Historical pro mode is retired; use the migration exercise in azure_execution/content_understanding.
The project teaches industry patterns with small data. The following still require environment
work: real end-user authentication, production-grade distributed state, managed identity from your
Databricks design, private networking, approved connectors, feature quota, CI federation and live
quality targets. They are not secretly implemented by fixture identities or small local tests.
