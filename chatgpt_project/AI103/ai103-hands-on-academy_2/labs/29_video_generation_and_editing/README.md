# Lab 29 — Video generation and editing

**Reviewed execution instructions:** start with [RUNBOOK.md](RUNBOOK.md). It lists exact widgets, secrets, variants and failure recovery.

**Prerequisites:** 28. **Execution:** local + Azure. **Handbook sections:** 24.1.
Allow roughly 30–90 minutes plus resource provisioning. Stop after the acceptance check before adding the extension.

## Understand the concept

Video generation is a long-running job. Persist the job ID, poll with a deadline, and retrieve the output only after success. Reference media can guide generation or edits.

## Set up once

Read [the setup guide](../../docs/setup/10_DOCUMENTS_AND_MEDIA.md) and [the Databricks guide](../../docs/setup/DATABRICKS.md).
Provision only the current service. The [source script](run.py) shows the exact imports, input and result.
Optional live dependencies are in `requirements/media.txt`; the Databricks notebook installs that set.
Cloud examples require your own resources and permissions. They have not been executed against your subscription.

## Execute in Databricks

1. Complete bootstrap and attach the compute described in the Databricks guide.
2. Import `databricks/labs/29_video_generation_and_editing.py` as a source notebook into Workspace.
3. Set project_root and a writable volume output_root. Keep live=false and run the lesson.
4. Inspect the printed JSON and its file in output_root. Read the called function in src/academy.
5. For the Azure/protocol path, finish setup, create the per-lab secrets, set live=true, install
   the lesson packages, restart Python, and run the final cell again. Portal-led/local-only labs
   state explicitly when --live is not an Azure implementation.
6. Use variant=default initially.

## Optional local commands

From the course root after the workstation setup:

```bash
python labs/29_video_generation_and_editing/run.py
python -m pip install -r requirements/media.txt
python labs/29_video_generation_and_editing/run.py --live
```

The last command applies only to implemented live paths; use the portal guide for portal-led labs.
Do not interpret an offline fixture, contract preview or local rule as a live AI result.

## Expected result and checkpoint

A printed job ID and outputs/generated.mp4 when the supported service finishes. Preview/access availability can block this lab.

Save one successful result and one failure example. Record the lab ID, model/service version,
settings changed and what you learned in [PROGRESS.csv](../../PROGRESS.csv).
You are ready to continue when you can identify the input, trust boundary, output and failure behavior.

## Experiment

Pass --file data/media/video_reference.png, then remix a completed video ID. Compare reference changes, supported resolution and duration. Edit with a new prompt and inspect temporal consistency.

## Explain before proceeding

Why does this design fit the requirement? What failure would you expect if one control were removed?
Give a 60-second answer before reading [INSTRUCTOR_NOTES.md](INSTRUCTOR_NOTES.md).

If blocked, use [troubleshooting](../../docs/TROUBLESHOOTING.md) and report the lab ID with a
sanitized error. Remove unused learning resources using [cleanup guidance](../../docs/CLEANUP.md).

Previous: [28 Image generation and mask editing](../28_image_generation_and_mask_editing/README.md) · Next: [30 Enterprise grounding and operational data](../30_enterprise_grounding_and_operational_data/README.md)

Reference-image experiment: use the included `data/media/video_reference.png` (1280x720). Upload it to your volume and set input_file to that path. It matches the default VIDEO_SIZE.
