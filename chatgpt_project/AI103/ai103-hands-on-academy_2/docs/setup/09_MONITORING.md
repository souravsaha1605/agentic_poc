# Observability evaluation and cost

## Application Insights

1. Azure Portal → create a Log Analytics workspace, then an Application Insights resource
   connected to it in the learning group. Record its connection string in the secret scope as
   applicationinsights-connection-string.
2. Run lab 22 live. The Azure Monitor OpenTelemetry distribution exports a parent request span
   and child retrieval span. Wait for ingestion, then use transaction search or Logs to find it.
3. Start with the queries in `observability/queries.kql`. Table names differ between workspace
   and classic resource query contexts (AppDependencies versus dependencies). Inspect the
   available schema first and adapt the query rather than assuming every context is identical.
4. Add durations for model/tool/search/memory, deployment/prompt version, token usage and safety
   outcome. Avoid raw prompts, credentials, PII and high-cardinality payloads as attributes.
5. Configure retention and sampling deliberately. Head sampling is set at request start; tail
   policies require an appropriate collector/backend. Keep critical security audit records in
   a suitable durable audit path rather than relying solely on sampled performance traces.

## Evaluation

Run lab 23 offline to understand the metric split. Its tiny dataset and deterministic router
are not evidence of model quality. Add labeled live traces: expected intent, expected tool and
arguments, permitted/forbidden action, relevant source IDs, answer requirements and abstention.
Capture model/prompt/index version. Add a held-out set and human review for ambiguous cases.

The optional live evaluator path uses the Azure AI Evaluation SDK in a separate dependency set.
It calls model-assisted groundedness and relevance evaluators with a compatible deployed judge.
In Foundry's evaluation UI, create a dataset/run and inspect supported agent evaluators for
intent, tool calls and adherence. Map your actual conversation/tool trace to the evaluator's
required input schema; an answer-only CSV cannot evaluate tool behavior. The requirements use
a documented SDK family; check installed-version compatibility if the service surface changes.

Version baseline results. Gate critical unauthorized actions at zero in the teaching suite;
set quality thresholds according to real requirements and uncertainty. The handbook's 95/99/90
figures are example project targets, not exam pass marks or universal acceptance criteria.
A red-team or evaluation run can incur model/service charges.

## Cost quotas and drift

In Azure Portal → Cost Management, create a budget scoped to the learning group with alerts
at thresholds you choose. Budgets are alerts, not automatic hard spending caps. Inspect each
model deployment's quota/capacity, 429 events and usage. Use lab 32's calculator with YOUR current
prices; the shipped values are deliberately fictional units. Add search, safety, storage,
monitoring, speech and media charges when estimating a full system.

Keep release-level dashboards for p50/p95 latency, error/429 rate, token/request distribution,
retrieval misses, ingestion lag, safety events and evaluation scores. When quality changes,
compare input mix and data freshness before attributing the change to the model. Use cache TTLs
and versioned keys, bounded concurrency and explicit queue limits. Do not “fix” sustained quota
exhaustion by increasing retries.

References:
- https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-enable?tabs=python
- https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/evaluate-sdk
