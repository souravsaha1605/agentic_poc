# Lab 17 — Agentic retrieval and knowledge tools

**Reviewed execution instructions:** start with [RUNBOOK.md](RUNBOOK.md). It lists exact widgets, secrets, variants and failure recovery.

**Prerequisites:** 11,12,16. **Execution:** local + Azure. **Handbook sections:** 7,8,13.
Allow roughly 30–90 minutes plus resource provisioning. Stop after the acceptance check before adding the extension.

## Understand the concept

With agentic retrieval the model chooses a search tool and its query; the backend still applies tenant scope. This differs from always retrieving before generation.

## Set up once

Read [the setup guide](../../docs/setup/05_SEARCH_AND_INGESTION.md) and [the Databricks guide](../../docs/setup/DATABRICKS.md).
Provision only the current service. The [source script](run.py) shows the exact imports, input and result.
Optional live dependencies are in `requirements/core.txt`; the Databricks notebook installs that set.
Cloud examples require your own resources and permissions. They have not been executed against your subscription.

## Execute in Databricks

1. Complete bootstrap and attach the compute described in the Databricks guide.
2. Import `databricks/labs/17_agentic_retrieval_and_knowledge_tools.py` as a source notebook into Workspace.
3. Set project_root and a writable volume output_root. Keep live=false and run the lesson.
4. Inspect the printed JSON and its file in output_root. Read the called function in src/academy.
5. For the Azure/protocol path, finish setup, create the per-lab secrets, set live=true, install
   the lesson packages, restart Python, and run the final cell again. Portal-led/local-only labs
   state explicitly when --live is not an Azure implementation.
6. Use variant=default initially.

## Optional local commands

From the course root after the workstation setup:

```bash
python labs/17_agentic_retrieval_and_knowledge_tools/run.py
python -m pip install -r requirements/core.txt
python labs/17_agentic_retrieval_and_knowledge_tools/run.py --live
```

The last command applies only to implemented live paths; use the portal guide for portal-led labs.
Do not interpret an offline fixture, contract preview or local rule as a live AI result.

## Expected result and checkpoint

Live mode may choose search_policy or answer without a tool. variant=default uses the local corpus; variant=azure-search uses the implemented Azure Search tool.

Save one successful result and one failure example. Record the lab ID, model/service version,
settings changed and what you learned in [PROGRESS.csv](../../PROGRESS.csv).
You are ready to continue when you can identify the input, trust boundary, output and failure behavior.

## Experiment

Use variant=azure-search after lab 09 ingestion; compare with variant=default using the local policy tool. Connect a permitted Azure Search index to the managed agent in Foundry and compare traces.

## Explain before proceeding

Why does this design fit the requirement? What failure would you expect if one control were removed?
Give a 60-second answer before reading [INSTRUCTOR_NOTES.md](INSTRUCTOR_NOTES.md).

If blocked, use [troubleshooting](../../docs/TROUBLESHOOTING.md) and report the lab ID with a
sanitized error. Remove unused learning resources using [cleanup guidance](../../docs/CLEANUP.md).

Previous: [16 Foundry managed agent](../16_foundry_managed_agent/README.md) · Next: [18 Sequential and concurrent workflows](../18_sequential_and_concurrent_workflows/README.md)
