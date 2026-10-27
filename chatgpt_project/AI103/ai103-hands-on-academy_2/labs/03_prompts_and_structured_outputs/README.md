# Lab 03 — Prompts and structured outputs

**Reviewed execution instructions:** start with [RUNBOOK.md](RUNBOOK.md). It lists exact widgets, secrets, variants and failure recovery.

**Prerequisites:** 02. **Execution:** local + Azure. **Handbook sections:** 9,10.
Allow roughly 30–90 minutes plus resource provisioning. Stop after the acceptance check before adding the extension.

## Understand the concept

System instructions define intended behavior. Native structured outputs and application validation make the output usable by software. Valid JSON can still contain unsupported facts.

## Set up once

Read [the setup guide](../../docs/setup/02_FOUNDRY_AND_MODELS.md) and [the Databricks guide](../../docs/setup/DATABRICKS.md).
Provision only the current service. The [source script](run.py) shows the exact imports, input and result.
Optional live dependencies are in `requirements/core.txt`; the Databricks notebook installs that set.
Cloud examples require your own resources and permissions. They have not been executed against your subscription.

## Execute in Databricks

1. Complete bootstrap and attach the compute described in the Databricks guide.
2. Import `databricks/labs/03_prompts_and_structured_outputs.py` as a source notebook into Workspace.
3. Set project_root and a writable volume output_root. Keep live=false and run the lesson.
4. Inspect the printed JSON and its file in output_root. Read the called function in src/academy.
5. For the Azure/protocol path, finish setup, create the per-lab secrets, set live=true, install
   the lesson packages, restart Python, and run the final cell again. Portal-led/local-only labs
   state explicitly when --live is not an Azure implementation.
6. Use variant=default initially.

## Optional local commands

From the course root after the workstation setup:

```bash
python labs/03_prompts_and_structured_outputs/run.py
python -m pip install -r requirements/core.txt
python labs/03_prompts_and_structured_outputs/run.py --live
```

The last command applies only to implemented live paths; use the portal guide for portal-led labs.
Do not interpret an offline fixture, contract preview or local rule as a live AI result.

## Expected result and checkpoint

Exactly answer, sources, uncertain; an unknown source ID raises ValueError.

Save one successful result and one failure example. Record the lab ID, model/service version,
settings changed and what you learned in [PROGRESS.csv](../../PROGRESS.csv).
You are ready to continue when you can identify the input, trust boundary, output and failure behavior.

## Experiment

Change the offline source ID to invented-v1. Add an unexpected field. Compare concise versus detailed prompt versions, and record the prompt version with results.

## Explain before proceeding

Why does this design fit the requirement? What failure would you expect if one control were removed?
Give a 60-second answer before reading [INSTRUCTOR_NOTES.md](INSTRUCTOR_NOTES.md).

If blocked, use [troubleshooting](../../docs/TROUBLESHOOTING.md) and report the lab ID with a
sanitized error. Remove unused learning resources using [cleanup guidance](../../docs/CLEANUP.md).

Previous: [02 Model calls and routing](../02_model_calls_and_routing/README.md) · Next: [04 Content Safety input and output](../04_content_safety_input_and_output/README.md)

Implemented next exercise: [generation controls](../../extensions/generation_controls/RUNBOOK.md).
