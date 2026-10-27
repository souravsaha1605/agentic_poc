# Lab 23 — Evaluation datasets and regression gates

**Reviewed execution instructions:** start with [RUNBOOK.md](RUNBOOK.md). It lists exact widgets, secrets, variants and failure recovery.

**Prerequisites:** 05,11,12,22. **Execution:** local + Azure. **Handbook sections:** 19,24.4.
Allow roughly 30–90 minutes plus resource provisioning. Stop after the acceptance check before adding the extension.

## Understand the concept

Intent, tool choice, policy adherence and groundedness diagnose different failures. A benchmark needs labeled inputs, expected behavior and held-out cases.

## Set up once

Read [the setup guide](../../docs/setup/09_MONITORING.md) and [the Databricks guide](../../docs/setup/DATABRICKS.md).
Provision only the current service. The [source script](run.py) shows the exact imports, input and result.
Optional live dependencies are in `requirements/evaluation.txt`; the Databricks notebook installs that set.
Cloud examples require your own resources and permissions. They have not been executed against your subscription.

## Execute in Databricks

1. Complete bootstrap and attach the compute described in the Databricks guide.
2. Import `databricks/labs/23_evaluation_datasets_and_regression_gates.py` as a source notebook into Workspace.
3. Set project_root and a writable volume output_root. Keep live=false and run the lesson.
4. Inspect the printed JSON and its file in output_root. Read the called function in src/academy.
5. For the Azure/protocol path, finish setup, create the per-lab secrets, set live=true, install
   the lesson packages, restart Python, and run the final cell again. Portal-led/local-only labs
   state explicitly when --live is not an Azure implementation.
6. Use variant=default initially.

## Optional local commands

From the course root after the workstation setup:

```bash
python labs/23_evaluation_datasets_and_regression_gates/run.py
python -m pip install -r requirements/evaluation.txt
python labs/23_evaluation_datasets_and_regression_gates/run.py --live
```

The last command applies only to implemented live paths; use the portal guide for portal-led labs.
Do not interpret an offline fixture, contract preview or local rule as a live AI result.

## Expected result and checkpoint

Separate metrics for the local dispatcher. Live mode calls model-assisted groundedness and relevance evaluators.

Save one successful result and one failure example. Record the lab ID, model/service version,
settings changed and what you learned in [PROGRESS.csv](../../PROGRESS.csv).
You are ready to continue when you can identify the input, trust boundary, output and failure behavior.

## Experiment

Add 20–30 labeled cases including ambiguous intent and forbidden orders. Capture actual live tool traces for tool-call accuracy. Compare prompts on a held-out set; do not tune on every evaluation case.

## Explain before proceeding

Why does this design fit the requirement? What failure would you expect if one control were removed?
Give a 60-second answer before reading [INSTRUCTOR_NOTES.md](INSTRUCTOR_NOTES.md).

If blocked, use [troubleshooting](../../docs/TROUBLESHOOTING.md) and report the lab ID with a
sanitized error. Remove unused learning resources using [cleanup guidance](../../docs/CLEANUP.md).

Previous: [22 Tracing and loop diagnostics](../22_tracing_and_loop_diagnostics/README.md) · Next: [24 Vision accessibility and visual safety](../24_vision_accessibility_and_visual_safety/README.md)

Implemented next exercise: [rag evaluation](../../extensions/rag_evaluation/RUNBOOK.md).
