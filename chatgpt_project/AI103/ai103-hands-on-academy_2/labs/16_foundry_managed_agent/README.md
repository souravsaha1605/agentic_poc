# Lab 16 — Foundry managed agent

**Reviewed execution instructions:** start with [RUNBOOK.md](RUNBOOK.md). It lists exact widgets, secrets, variants and failure recovery.

**Prerequisites:** 02,12,15. **Execution:** local + Azure. **Handbook sections:** 12,20,23.
Allow roughly 30–90 minutes plus resource provisioning. Stop after the acceptance check before adding the extension.

## Understand the concept

A Foundry prompt agent persists a versioned definition and can use a conversation for multi-turn interaction. This is a managed service, distinct from the local tool loop.

## Set up once

Read [the setup guide](../../docs/setup/02_FOUNDRY_AND_MODELS.md) and [the Databricks guide](../../docs/setup/DATABRICKS.md).
Provision only the current service. The [source script](run.py) shows the exact imports, input and result.
Optional live dependencies are in `requirements/agents.txt`; the Databricks notebook installs that set.
Cloud examples require your own resources and permissions. They have not been executed against your subscription.

## Execute in Databricks

1. Complete bootstrap and attach the compute described in the Databricks guide.
2. Import `databricks/labs/16_foundry_managed_agent.py` as a source notebook into Workspace.
3. Set project_root and a writable volume output_root. Keep live=false and run the lesson.
4. Inspect the printed JSON and its file in output_root. Read the called function in src/academy.
5. For the Azure/protocol path, finish setup, create the per-lab secrets, set live=true, install
   the lesson packages, restart Python, and run the final cell again. Portal-led/local-only labs
   state explicitly when --live is not an Azure implementation.
6. Use variant=default initially.

## Optional local commands

From the course root after the workstation setup:

```bash
python labs/16_foundry_managed_agent/run.py
python -m pip install -r requirements/agents.txt
python labs/16_foundry_managed_agent/run.py --live
```

The last command applies only to implemented live paths; use the portal guide for portal-led labs.
Do not interpret an offline fixture, contract preview or local rule as a live AI result.

## Expected result and checkpoint

The second response recalls K100. The agent version remains for portal inspection; the sample conversation is deleted.

Save one successful result and one failure example. Record the lab ID, model/service version,
settings changed and what you learned in [PROGRESS.csv](../../PROGRESS.csv).
You are ready to continue when you can identify the input, trust boundary, output and failure behavior.

## Experiment

Start a new conversation and repeat the recall question. Inspect the version in Foundry. Change instructions, create another version and compare behavior.

## Explain before proceeding

Why does this design fit the requirement? What failure would you expect if one control were removed?
Give a 60-second answer before reading [INSTRUCTOR_NOTES.md](INSTRUCTOR_NOTES.md).

If blocked, use [troubleshooting](../../docs/TROUBLESHOOTING.md) and report the lab ID with a
sanitized error. Remove unused learning resources using [cleanup guidance](../../docs/CLEANUP.md).

Previous: [15 Memory windows Redis and Cosmos](../15_memory_windows_redis_and_cosmos/README.md) · Next: [17 Agentic retrieval and knowledge tools](../17_agentic_retrieval_and_knowledge_tools/README.md)
