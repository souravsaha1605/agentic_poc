# Lab 15 — Memory windows Redis and Cosmos

**Reviewed execution instructions:** start with [RUNBOOK.md](RUNBOOK.md). It lists exact widgets, secrets, variants and failure recovery.

**Prerequisites:** 13. **Execution:** local + Azure. **Handbook sections:** 20.
Allow roughly 30–90 minutes plus resource provisioning. Stop after the acceptance check before adding the extension.

## Understand the concept

Models do not retain arbitrary prior API calls. The application supplies conversation state. Session TTL and durable preferences need different retention policies.

## Set up once

Read [the setup guide](../../docs/setup/06_MEMORY_AND_ENTERPRISE.md) and [the Databricks guide](../../docs/setup/DATABRICKS.md).
Provision only the current service. The [source script](run.py) shows the exact imports, input and result.
Optional live dependencies are in `requirements/memory.txt`; the Databricks notebook installs that set.
Cloud examples require your own resources and permissions. They have not been executed against your subscription.

## Execute in Databricks

1. Complete bootstrap and attach the compute described in the Databricks guide.
2. Import `databricks/labs/15_memory_windows_redis_and_cosmos.py` as a source notebook into Workspace.
3. Set project_root and a writable volume output_root. Keep live=false and run the lesson.
4. Inspect the printed JSON and its file in output_root. Read the called function in src/academy.
5. For the Azure/protocol path, finish setup, create the per-lab secrets, set live=true, install
   the lesson packages, restart Python, and run the final cell again. Portal-led/local-only labs
   state explicitly when --live is not an Azure implementation.
6. For cloud storage choose variant=redis or variant=cosmos. Other variants are rejected.

## Optional local commands

From the course root after the workstation setup:

```bash
python labs/15_memory_windows_redis_and_cosmos/run.py
python -m pip install -r requirements/memory.txt
python labs/15_memory_windows_redis_and_cosmos/run.py --live --variant redis
```

The last command applies only to implemented live paths; use the portal guide for portal-led labs.
Do not interpret an offline fixture, contract preview or local rule as a live AI result.

## Expected result and checkpoint

Alice sees her session; Bob sees an empty list. Live examples create and remove synthetic records.

Save one successful result and one failure example. Record the lab ID, model/service version,
settings changed and what you learned in [PROGRESS.csv](../../PROGRESS.csv).
You are ready to continue when you can identify the input, trust boundary, output and failure behavior.

## Experiment

Expire a session. Compare last-N messages, a token budget and a summary. Ask what a summary might lose. Add a delete-memory operation and test it.

## Explain before proceeding

Why does this design fit the requirement? What failure would you expect if one control were removed?
Give a 60-second answer before reading [INSTRUCTOR_NOTES.md](INSTRUCTOR_NOTES.md).

If blocked, use [troubleshooting](../../docs/TROUBLESHOOTING.md) and report the lab ID with a
sanitized error. Remove unused learning resources using [cleanup guidance](../../docs/CLEANUP.md).

Previous: [14 Retries idempotency and caching](../14_retries_idempotency_and_caching/README.md) · Next: [16 Foundry managed agent](../16_foundry_managed_agent/README.md)

## Additional Databricks variation

Import `databricks/extensions/15_memory_summary.py` after this lab. Read the matching extension code and setup before using live=true.
