# Lab 25 — Document Intelligence receipts and layout

**Reviewed execution instructions:** start with [RUNBOOK.md](RUNBOOK.md). It lists exact widgets, secrets, variants and failure recovery.

**Prerequisites:** 24. **Execution:** local + Azure. **Handbook sections:** 21.
Allow roughly 30–90 minutes plus resource provisioning. Stop after the acceptance check before adding the extension.

## Understand the concept

Business documents need fields, tables, layout and provenance. Validate extracted values before using them to make a business decision.

## Set up once

Read [the setup guide](../../docs/setup/10_DOCUMENTS_AND_MEDIA.md) and [the Databricks guide](../../docs/setup/DATABRICKS.md).
Provision only the current service. The [source script](run.py) shows the exact imports, input and result.
Optional live dependencies are in `requirements/documents.txt`; the Databricks notebook installs that set.
Cloud examples require your own resources and permissions. They have not been executed against your subscription.

## Execute in Databricks

1. Complete bootstrap and attach the compute described in the Databricks guide.
2. Import `databricks/labs/25_document_intelligence_receipts_and_layout.py` as a source notebook into Workspace.
3. Set project_root and a writable volume output_root. Keep live=false and run the lesson.
4. Inspect the printed JSON and its file in output_root. Read the called function in src/academy.
5. For the Azure/protocol path, finish setup, create the per-lab secrets, set live=true, install
   the lesson packages, restart Python, and run the final cell again. Portal-led/local-only labs
   state explicitly when --live is not an Azure implementation.
6. variant=layout compares layout extraction with prebuilt receipt fields.

## Optional local commands

From the course root after the workstation setup:

```bash
python labs/25_document_intelligence_receipts_and_layout/run.py
python -m pip install -r requirements/documents.txt
python labs/25_document_intelligence_receipts_and_layout/run.py --live
```

The last command applies only to implemented live paths; use the portal guide for portal-led labs.
Do not interpret an offline fixture, contract preview or local rule as a live AI result.

## Expected result and checkpoint

Extracted receipt fields or page/table structure. Offline fields are explicitly synthetic fixtures.

Save one successful result and one failure example. Record the lab ID, model/service version,
settings changed and what you learned in [PROGRESS.csv](../../PROGRESS.csv).
You are ready to continue when you can identify the input, trust boundary, output and failure behavior.

## Experiment

Run --variant layout and compare fields with receipt mode. Blur a copy locally with an image editor and compare confidence. In Document Intelligence Studio, label a small custom model dataset and inspect train/test separation.

## Explain before proceeding

Why does this design fit the requirement? What failure would you expect if one control were removed?
Give a 60-second answer before reading [INSTRUCTOR_NOTES.md](INSTRUCTOR_NOTES.md).

If blocked, use [troubleshooting](../../docs/TROUBLESHOOTING.md) and report the lab ID with a
sanitized error. Remove unused learning resources using [cleanup guidance](../../docs/CLEANUP.md).

Previous: [24 Vision accessibility and visual safety](../24_vision_accessibility_and_visual_safety/README.md) · Next: [26 Content Understanding analyzers](../26_content_understanding_analyzers/README.md)

For the OCR comparison, set variant=read to use prebuilt-read. Compare extracted text with variant=layout and the default receipt fields; they answer different questions.
