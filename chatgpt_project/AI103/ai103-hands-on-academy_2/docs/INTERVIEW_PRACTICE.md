# Explain what you built

After each lab, give a 60–90 second answer using requirement → choice → trade-off → control →
measurement. Use your actual run evidence, including failures. Do not say a fixture exercised Azure.

| Scenario | What a strong answer includes |
|---|---|
| Refund assistant | Identity/ownership, eligibility, approval threshold, immutable request, idempotency, audit |
| Multilingual support | Language detection, PII boundary, translation fidelity, retrieval, speech errors, human escalation |
| Enterprise research | Source shape/freshness, tenant scope, analytical versus operational truth, citations |
| High-volume FAQ | Small/large model comparison, cache isolation/TTL, quota, bounded fan-out, p95 and quality |
| New prompt rollout | Versioned prompt/schema, held-out benchmark, adversarial tests, deployment gate, rollback |
| Slow agent | Trace stage breakdown, dependent versus independent calls, loops, cache misses, token/context growth |
| Incorrect grounded answer | Separate ingestion, retrieval, source support, generation and output validation failures |
| Credentials in Databricks | Secret scope versus SDK identity, exact principal/role, driver boundaries, no secret broadcast |

Explain without reading code:

1. Why isn't valid JSON evidence of a correct answer?
2. Why can't a successful token acquisition prove authorization?
3. What makes a tool retry safe after an uncertain timeout?
4. What can a summary forget or preserve incorrectly?
5. How does semantic reranking differ from vector similarity?
6. Why doesn't a partition key establish a security boundary?
7. When would you choose one agent instead of a manager and specialists?
8. Why do approval state and HTTP request lifetime need different handling?
9. Why might an image-generation model be the wrong choice for OCR?
10. What would you change before serving real customers from this teaching application?

Model answer for question 3: use a durable request key bound to an immutable operation. On a
timeout, inspect the operation status. The downstream action provider must deduplicate retries;
a local log entry alone cannot prevent a duplicate external charge. Monitor reconciliation gaps.

Model answer for question 10: validate real identity, authorize user/data/tool access, use durable
state with concurrency control, narrow cloud roles, approved networking, retention/redaction,
representative quality/safety gates, capacity management and operational recovery. Then demonstrate
these controls with failure tests rather than merely listing products.
