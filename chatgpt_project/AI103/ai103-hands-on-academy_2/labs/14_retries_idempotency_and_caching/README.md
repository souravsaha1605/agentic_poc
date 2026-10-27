# Lab 14 — Retries idempotency and caching

**Reviewed execution instructions:** start with [RUNBOOK.md](RUNBOOK.md). It lists exact widgets, secrets, variants and failure recovery.

**Prerequisites:** 12,13. **Execution:** local. **Handbook sections:** 6,14.
Allow roughly 30–90 minutes plus resource provisioning. Stop after the acceptance check before adding the extension.

## Understand the concept

Retries are safe only when the effect is controlled. An idempotency key identifies one business request and must reject a conflicting payload. Cache keys include user/tenant and policy version.

## Set up once

Read [the setup guide](../../docs/TROUBLESHOOTING.md) and [the Databricks guide](../../docs/setup/DATABRICKS.md).
Provision only the current service. The [source script](run.py) shows the exact imports, input and result.
Optional live dependencies are in `requirements/core.txt`; the Databricks notebook installs that set.
Cloud examples require your own resources and permissions. They have not been executed against your subscription.

## Execute in Databricks

1. Complete bootstrap and attach the compute described in the Databricks guide.
2. Import `databricks/labs/14_retries_idempotency_and_caching.py` as a source notebook into Workspace.
3. Set project_root and a writable volume output_root. Keep live=false and run the lesson.
4. Inspect the printed JSON and its file in output_root. Read the called function in src/academy.
5. Keep live=false for this local lesson. If it has a separate portal exercise, follow RUNBOOK.md and azure_execution; this script does not implement a live Azure branch.
6. Use variant=default initially.

## Optional local commands

From the course root after the workstation setup:

```bash
python labs/14_retries_idempotency_and_caching/run.py
```

The last command applies only to implemented live paths; use the portal guide for portal-led labs.
Do not interpret an offline fixture, contract preview or local rule as a live AI result.

## Expected result and checkpoint

Both calls report executed, but the effect count stays 1; no payment is made.

Save one successful result and one failure example. Record the lab ID, model/service version,
settings changed and what you learned in [PROGRESS.csv](../../PROGRESS.csv).
You are ready to continue when you can identify the input, trust boundary, output and failure behavior.

## Experiment

Reuse a key with a different order/user and expect rejection. Set cache TTL=0 and verify a miss. Inspect cloud.request for bounded read retries and Retry-After behavior.

## Explain before proceeding

Why does this design fit the requirement? What failure would you expect if one control were removed?
Give a 60-second answer before reading [INSTRUCTOR_NOTES.md](INSTRUCTOR_NOTES.md).

If blocked, use [troubleshooting](../../docs/TROUBLESHOOTING.md) and report the lab ID with a
sanitized error. Remove unused learning resources using [cleanup guidance](../../docs/CLEANUP.md).

Previous: [13 Dynamic instructions and authorization](../13_dynamic_instructions_and_authorization/README.md) · Next: [15 Memory windows Redis and Cosmos](../15_memory_windows_redis_and_cosmos/README.md)
