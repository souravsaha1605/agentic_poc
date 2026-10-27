# Lab 06 — Language and PII preprocessing

**Reviewed execution instructions:** start with [RUNBOOK.md](RUNBOOK.md). It lists exact widgets, secrets, variants and failure recovery.

**Prerequisites:** 04. **Execution:** local + Azure. **Handbook sections:** 22.
Allow roughly 30–90 minutes plus resource provisioning. Stop after the acceptance check before adding the extension.

## Understand the concept

Dedicated language analysis can detect language, redact PII, extract entities/key phrases and classify sentiment before the model boundary.

## Set up once

Read [the setup guide](../../docs/setup/04_LANGUAGE_AND_SPEECH.md) and [the Databricks guide](../../docs/setup/DATABRICKS.md).
Provision only the current service. The [source script](run.py) shows the exact imports, input and result.
Optional live dependencies are in `requirements/language.txt`; the Databricks notebook installs that set.
Cloud examples require your own resources and permissions. They have not been executed against your subscription.

## Execute in Databricks

1. Complete bootstrap and attach the compute described in the Databricks guide.
2. Import `databricks/labs/06_language_and_pii_preprocessing.py` as a source notebook into Workspace.
3. Set project_root and a writable volume output_root. Keep live=false and run the lesson.
4. Inspect the printed JSON and its file in output_root. Read the called function in src/academy.
5. For the Azure/protocol path, finish setup, create the per-lab secrets, set live=true, install
   the lesson packages, restart Python, and run the final cell again. Portal-led/local-only labs
   state explicitly when --live is not an Azure implementation.
6. Use variant=default initially.

## Optional local commands

From the course root after the workstation setup:

```bash
python labs/06_language_and_pii_preprocessing/run.py
python -m pip install -r requirements/language.txt
python labs/06_language_and_pii_preprocessing/run.py --live
```

The last command applies only to implemented live paths; use the portal guide for portal-led labs.
Do not interpret an offline fixture, contract preview or local rule as a live AI result.

## Expected result and checkpoint

Live service output contains redacted text and categories. Offline mode is a labeled saved example.

Save one successful result and one failure example. Record the lab ID, model/service version,
settings changed and what you learned in [PROGRESS.csv](../../PROGRESS.csv).
You are ready to continue when you can identify the input, trust boundary, output and failure behavior.

## Experiment

Try Hindi and mixed-language input. Check supported languages per operation. Inspect whether the redaction misses an order ID; add a domain-specific rule if needed.

## Explain before proceeding

Why does this design fit the requirement? What failure would you expect if one control were removed?
Give a 60-second answer before reading [INSTRUCTOR_NOTES.md](INSTRUCTOR_NOTES.md).

If blocked, use [troubleshooting](../../docs/TROUBLESHOOTING.md) and report the lab ID with a
sanitized error. Remove unused learning resources using [cleanup guidance](../../docs/CLEANUP.md).

Previous: [05 Prompt injection and red teaming](../05_prompt_injection_and_red_teaming/README.md) · Next: [07 Translation and multilingual flow](../07_translation_and_multilingual_flow/README.md)

Implemented next exercise: [domain extraction](../../extensions/domain_extraction/RUNBOOK.md).
