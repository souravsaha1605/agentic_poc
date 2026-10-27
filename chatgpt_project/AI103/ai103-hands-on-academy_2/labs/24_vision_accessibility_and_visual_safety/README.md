# Lab 24 — Vision accessibility and visual safety

**Reviewed execution instructions:** start with [RUNBOOK.md](RUNBOOK.md). It lists exact widgets, secrets, variants and failure recovery.

**Prerequisites:** 04,05,02. **Execution:** local + Azure. **Handbook sections:** 21,24.2.
Allow roughly 30–90 minutes plus resource provisioning. Stop after the acceptance check before adding the extension.

## Understand the concept

Visual understanding describes visible evidence. OCR extracts characters; it does not determine the full meaning of a scene. Images can contain injected instructions.

## Set up once

Read [the setup guide](../../docs/setup/10_DOCUMENTS_AND_MEDIA.md) and [the Databricks guide](../../docs/setup/DATABRICKS.md).
Provision only the current service. The [source script](run.py) shows the exact imports, input and result.
Optional live dependencies are in `requirements/core.txt`; the Databricks notebook installs that set.
Cloud examples require your own resources and permissions. They have not been executed against your subscription.

## Execute in Databricks

1. Complete bootstrap and attach the compute described in the Databricks guide.
2. Import `databricks/labs/24_vision_accessibility_and_visual_safety.py` as a source notebook into Workspace.
3. Set project_root and a writable volume output_root. Keep live=false and run the lesson.
4. Inspect the printed JSON and its file in output_root. Read the called function in src/academy.
5. For the Azure/protocol path, finish setup, create the per-lab secrets, set live=true, install
   the lesson packages, restart Python, and run the final cell again. Portal-led/local-only labs
   state explicitly when --live is not an Azure implementation.
6. Use variant=default initially.

## Optional local commands

From the course root after the workstation setup:

```bash
python labs/24_vision_accessibility_and_visual_safety/run.py
python -m pip install -r requirements/core.txt
python labs/24_vision_accessibility_and_visual_safety/run.py --live
```

The last command applies only to implemented live paths; use the portal guide for portal-led labs.
Do not interpret an offline fixture, contract preview or local rule as a live AI result.

## Expected result and checkpoint

Alt text and a longer description grounded in the supplied image, plus visual moderation results.

Save one successful result and one failure example. Record the lab ID, model/service version,
settings changed and what you learned in [PROGRESS.csv](../../PROGRESS.csv).
You are ready to continue when you can identify the input, trust boundary, output and failure behavior.

## Experiment

Use receipt.png to compare OCR-like output with a caption. Add harmless text that asks the model to change its task and inspect behavior. Check unsupported claims about hidden damage.

## Explain before proceeding

Why does this design fit the requirement? What failure would you expect if one control were removed?
Give a 60-second answer before reading [INSTRUCTOR_NOTES.md](INSTRUCTOR_NOTES.md).

If blocked, use [troubleshooting](../../docs/TROUBLESHOOTING.md) and report the lab ID with a
sanitized error. Remove unused learning resources using [cleanup guidance](../../docs/CLEANUP.md).

Previous: [23 Evaluation datasets and regression gates](../23_evaluation_datasets_and_regression_gates/README.md) · Next: [25 Document Intelligence receipts and layout](../25_document_intelligence_receipts_and_layout/README.md)

Implemented next exercise: [visual evidence](../../extensions/visual_evidence/RUNBOOK.md).
