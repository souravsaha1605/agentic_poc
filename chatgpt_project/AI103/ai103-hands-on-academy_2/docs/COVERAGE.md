# Curriculum and coverage

This map is based on the supplied handbook; the current Microsoft study guide was checked on 22 October 2026. Exact exam objectives can change. The course covers concepts with code, service labs or explicitly marked portal exercises; it does not claim all Azure features were deployed here.

## Incremental curriculum

| Lab | Topic | Execution | Depends on |
|---|---|---|---|
| 00 | [Environment and project tour](../labs/00_environment_and_project_tour/README.md) | local | None |
| 01 | [Secrets identity and Key Vault](../labs/01_secrets_identity_and_key_vault/README.md) | local + Azure | 00 |
| 02 | [Model calls and routing](../labs/02_model_calls_and_routing/README.md) | local + Azure | 01 |
| 03 | [Prompts and structured outputs](../labs/03_prompts_and_structured_outputs/README.md) | local + Azure | 02 |
| 04 | [Content Safety input and output](../labs/04_content_safety_input_and_output/README.md) | local + Azure | 02 |
| 05 | [Prompt injection and red teaming](../labs/05_prompt_injection_and_red_teaming/README.md) | local + Azure | 04 |
| 06 | [Language and PII preprocessing](../labs/06_language_and_pii_preprocessing/README.md) | local + Azure | 04 |
| 07 | [Translation and multilingual flow](../labs/07_translation_and_multilingual_flow/README.md) | local + Azure | 06 |
| 08 | [Embeddings and chunking](../labs/08_embeddings_and_chunking/README.md) | local + Azure | 02 |
| 09 | [Azure Search vector hybrid semantic](../labs/09_azure_search_vector_hybrid_semantic/README.md) | local + Azure | 08 |
| 10 | [Ingestion OCR and enrichment](../labs/10_ingestion_ocr_and_enrichment/README.md) | local + portal | 09 |
| 11 | [Grounded answers with RAG](../labs/11_grounded_answers_with_rag/README.md) | local + Azure | 03,04,05,09 |
| 12 | [Function calling and REST contracts](../labs/12_function_calling_and_rest_contracts/README.md) | local + Azure | 03 |
| 13 | [Dynamic instructions and authorization](../labs/13_dynamic_instructions_and_authorization/README.md) | local | 12 |
| 14 | [Retries idempotency and caching](../labs/14_retries_idempotency_and_caching/README.md) | local | 12,13 |
| 15 | [Memory windows Redis and Cosmos](../labs/15_memory_windows_redis_and_cosmos/README.md) | local + Azure | 13 |
| 16 | [Foundry managed agent](../labs/16_foundry_managed_agent/README.md) | local + Azure | 02,12,15 |
| 17 | [Agentic retrieval and knowledge tools](../labs/17_agentic_retrieval_and_knowledge_tools/README.md) | local + Azure | 11,12,16 |
| 18 | [Sequential and concurrent workflows](../labs/18_sequential_and_concurrent_workflows/README.md) | local | 12 |
| 19 | [Multi agent orchestration and reflection](../labs/19_multi_agent_orchestration_and_reflection/README.md) | local + Azure | 12,17,18 |
| 20 | [Human approvals and Logic Apps](../labs/20_human_approvals_and_logic_apps/README.md) | local + portal | 13,14 |
| 21 | [MCP server and client](../labs/21_mcp_server_and_client/README.md) | local protocol | 12,13 |
| 22 | [Tracing and loop diagnostics](../labs/22_tracing_and_loop_diagnostics/README.md) | local + Azure | 12,18 |
| 23 | [Evaluation datasets and regression gates](../labs/23_evaluation_datasets_and_regression_gates/README.md) | local + Azure | 05,11,12,22 |
| 24 | [Vision accessibility and visual safety](../labs/24_vision_accessibility_and_visual_safety/README.md) | local + Azure | 04,05,02 |
| 25 | [Document Intelligence receipts and layout](../labs/25_document_intelligence_receipts_and_layout/README.md) | local + Azure | 24 |
| 26 | [Content Understanding analyzers](../labs/26_content_understanding_analyzers/README.md) | local + Azure | 25,10 |
| 27 | [Speech transcription synthesis translation](../labs/27_speech_transcription_synthesis_translation/README.md) | local + Azure | 06,07 |
| 28 | [Image generation and mask editing](../labs/28_image_generation_and_mask_editing/README.md) | local + Azure | 24 |
| 29 | [Video generation and editing](../labs/29_video_generation_and_editing/README.md) | local + Azure | 28 |
| 30 | [Enterprise grounding and operational data](../labs/30_enterprise_grounding_and_operational_data/README.md) | local + Azure | 09,15 |
| 31 | [Infrastructure deployment and CI CD](../labs/31_infrastructure_deployment_and_ci_cd/README.md) | local + portal/CLI | 01,16,22,23 |
| 32 | [Cost quotas scaling and drift](../labs/32_cost_quotas_scaling_and_drift/README.md) | local + portal | 02,14,22,23 |

## Handbook crosswalk

| Handbook section | Implementation and exercise |
|---|---|
| 1 | 01,13,22 — identity, secret access, permission boundaries and distinct audit stages |
| 2 | 04,24 — input/output and visual safety |
| 3 | 05,11,24 — direct, document and image instruction attacks |
| 4 | 05,23,31 — adversarial cases, portal red teaming, regression gates |
| 5 | 02,32 — measured model selection and routing |
| 6 | 02,14,32 — deployment, quotas, bounded retries, cache and cost |
| 7 | 08–11,17 — chunking, embeddings, retrieval, RAG and agent-selected search |
| 8 | 09,30 — Search, Cosmos vector extension, Fabric/OneLake SQL exercise |
| 9 | 03,11 — prompt contracts and evidence rules |
| 10 | 03,11 — structured outputs, validation and abstention |
| 11 | 13 — trusted role/state prompt construction and tool lists |
| 12 | 16,19 — managed agent, manager/handoff and group_chat.py |
| 13 | 12,17; extensions/rest_tools — function calls and HTTP contracts |
| 14 | 14,20 — deduplication, expiry, retry and state transitions |
| 15 | 21 — real local MCP discovery/invocation |
| 16 | 18,19; capstone 04 — sequential, concurrent and role-based orchestration |
| 17 | 20; extensions/approvals — state machine and Logic Apps portal workflow |
| 18 | 22 — OpenTelemetry, loop detection, KQL and sampling discussion |
| 19 | 23,31 — ground truth, metric separation, judge examples and CI gates |
| 20 | 15; summarize.py — TTL, scoped memory, Redis/Cosmos and summarization |
| 21 | 24–27 — visual understanding, receipt/layout, speech/SSML and extraction |
| 22 | 06,07,27; capstone 03 — language, PII, entities, sentiment and translation |
| 23 | 00,31; all capstones — layered architecture, Python/REST/async, Bicep and deployment |
| 24.1 | 28–29 — generated images/video, masks and reference editing |
| 24.2 | 24–26 — captions, regions, accessibility, Content Understanding and media analyzers |
| 24.3 | 07,27; capstone 03 — text and speech translation |
| 24.4 | 23 — groundedness/relevance and agent behavior evaluation |
| 24.5 | 31 — versioning, quality gates, deployment and rollback |
| 24.6 | 19 — bounded critique/revision and observable decision evaluation |

## Official exam domains

| Domain | Weight | Main lessons |
|---|---|---|
| Plan and manage | 25–30% | 01–05,13–14,20,22–23,31–32 |
| Generative AI and agents | 30–35% | 02–03,08–19,21–23 |
| Computer vision | 10–15% | 24,26,28–29 |
| Text analysis | 10–15% | 06–07,27 |
| Information extraction | 10–15% | 08–11,25–26 |

## Detailed coverage and deliberate limits

- Model families, code tasks and multimodal selection: lab 02 experiments and 24/28/29; availability is deployment-specific.
- Knowledge/memory/tool integration: 09,12,15–17,21,30. Managed-agent tools require the supported portal/SDK connector configuration.
- Infrastructure, deployment types, CI/CD, private networking and roles: guides 01/02/11 and lab 31. Private networking is a guided portal exercise, not preprovisioned in Bicep.
- Model quality, safety events, drift, ingestion/index health and costs: 05,10,22–23,32.
- Trace provenance, oversight, approvals and constrained actions: 12–14,20,22.
- Workflows, model/rules combinations, reflection and multi-agent patterns: 12,17–19 and capstones.
- Visual captions, Q&A, objects/regions, accessibility, visual policy and embedded attacks: 24/26.
- Image/video creation, references, masks and edits: 28/29; preview contracts must match the chosen deployment.
- GA Content Understanding and current agentic document mode: 26 and extensions. Historical pro mode is retired; see the migration exercise.
- Entities/topics, summaries, tone/sentiment, sensitive content, structured JSON and domain customization: 03/06/07/15.
- Speech input/output, SSML, custom speech, audio reasoning and translation: 26/27 and guide 04.
- Multimodal ingestion, semantic/vector/hybrid retrieval, built-in/custom enrichment, OCR/layout and grounded markdown: 08–11,25–26 and custom skill extension.

## Handbook clarifications

Model size is not a guarantee of capability. The content-safety score scale must be selected explicitly. The handbook metric thresholds are examples, not exam criteria. The NLP preprocessing order is a useful pattern, not a universal rule. Speech confidence depends on API/result format. Cosmos partitioning is not authorization. Current Foundry role names can differ from older Azure AI names. MCP v1 and v2 examples are incompatible without migration. Reflection evaluates visible outputs/actions; it does not require hidden internal chain-of-thought.

Official source: https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-103

## Reviewed evidence paths

See [OBJECTIVE_EVIDENCE.md](OBJECTIVE_EVIDENCE.md) for implemented extensions and service-hosted exercises, and [EXECUTION_MATRIX.md](EXECUTION_MATRIX.md) for execution locations.
