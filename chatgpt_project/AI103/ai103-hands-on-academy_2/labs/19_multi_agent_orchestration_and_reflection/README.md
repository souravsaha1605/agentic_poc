# Lab 19 — Multi agent orchestration and reflection

**Reviewed execution instructions:** start with [RUNBOOK.md](RUNBOOK.md). It lists exact widgets, secrets, variants and failure recovery.

**Prerequisites:** 12,17,18. **Execution:** local + Azure. **Handbook sections:** 12,16,24.6.
Allow roughly 30–90 minutes plus resource provisioning. Stop after the acceptance check before adding the extension.

## Understand the concept

Separate roles and tool permissions when specialization helps. Manager, handoff and group discussion have different state flows. Reflection is a bounded review, not proof of correctness.

## Set up once

Read [the setup guide](../../docs/setup/02_FOUNDRY_AND_MODELS.md) and [the Databricks guide](../../docs/setup/DATABRICKS.md).
Provision only the current service. The [source script](run.py) shows the exact imports, input and result.
Optional live dependencies are in `requirements/core.txt`; the Databricks notebook installs that set.
Cloud examples require your own resources and permissions. They have not been executed against your subscription.

## Execute in Databricks

1. Complete bootstrap and attach the compute described in the Databricks guide.
2. Import `databricks/labs/19_multi_agent_orchestration_and_reflection.py` as a source notebook into Workspace.
3. Set project_root and a writable volume output_root. Keep live=false and run the lesson.
4. Inspect the printed JSON and its file in output_root. Read the called function in src/academy.
5. For the Azure/protocol path, finish setup, create the per-lab secrets, set live=true, install
   the lesson packages, restart Python, and run the final cell again. Portal-led/local-only labs
   state explicitly when --live is not an Azure implementation.
6. Use variant=default initially.

## Optional local commands

From the course root after the workstation setup:

```bash
python labs/19_multi_agent_orchestration_and_reflection/run.py
python -m pip install -r requirements/core.txt
python labs/19_multi_agent_orchestration_and_reflection/run.py --live
```

The last command applies only to implemented live paths; use the portal guide for portal-led labs.
Do not interpret an offline fixture, contract preview or local rule as a live AI result.

## Expected result and checkpoint

Three bounded stages: draft, review, revision. --variant handoff passes an explicit state object to a specialist.

Save one successful result and one failure example. Record the lab ID, model/service version,
settings changed and what you learned in [PROGRESS.csv](../../PROGRESS.csv).
You are ready to continue when you can identify the input, trust boundary, output and failure behavior.

## Experiment

Compare final quality and latency with one model call. Implement a two-round group discussion with a fixed speaker order and stop condition. Give specialists disjoint tool lists.

## Explain before proceeding

Why does this design fit the requirement? What failure would you expect if one control were removed?
Give a 60-second answer before reading [INSTRUCTOR_NOTES.md](INSTRUCTOR_NOTES.md).

If blocked, use [troubleshooting](../../docs/TROUBLESHOOTING.md) and report the lab ID with a
sanitized error. Remove unused learning resources using [cleanup guidance](../../docs/CLEANUP.md).

Previous: [18 Sequential and concurrent workflows](../18_sequential_and_concurrent_workflows/README.md) · Next: [20 Human approvals and Logic Apps](../20_human_approvals_and_logic_apps/README.md)

## Additional Databricks variation

Import `databricks/extensions/19_group_discussion.py` after this lab. Read the matching extension code and setup before using live=true.
