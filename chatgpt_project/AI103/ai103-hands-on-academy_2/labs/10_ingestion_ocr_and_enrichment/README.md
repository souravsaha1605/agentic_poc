# Lab 10 — Ingestion OCR and enrichment

**Reviewed execution instructions:** start with [RUNBOOK.md](RUNBOOK.md). It lists exact widgets, secrets, variants and failure recovery.

**Prerequisites:** 09. **Execution:** local + portal. **Handbook sections:** 7,8,21,24.2.
Allow roughly 30–90 minutes plus resource provisioning. Stop after the acceptance check before adding the extension.

## Understand the concept

Indexers move source data; skillsets enrich it; indexes serve queries. Extraction, chunk IDs, updates and deleted records all affect grounding freshness.

## Set up once

Read [the setup guide](../../docs/setup/05_SEARCH_AND_INGESTION.md) and [the Databricks guide](../../docs/setup/DATABRICKS.md).
Provision only the current service. The [source script](run.py) shows the exact imports, input and result.
Optional live dependencies are in `requirements/core.txt`; the Databricks notebook installs that set.
Cloud examples require your own resources and permissions. They have not been executed against your subscription.

## Execute in Databricks

1. Complete bootstrap and attach the compute described in the Databricks guide.
2. Import `databricks/labs/10_ingestion_ocr_and_enrichment.py` as a source notebook into Workspace.
3. Set project_root and a writable volume output_root. Keep live=false and run the lesson.
4. Inspect the printed JSON and its file in output_root. Read the called function in src/academy.
5. Keep live=false for this local lesson. If it has a separate portal exercise, follow RUNBOOK.md and azure_execution; this script does not implement a live Azure branch.
6. Use variant=default initially.

## Optional local commands

From the course root after the workstation setup:

```bash
python labs/10_ingestion_ocr_and_enrichment/run.py
```

The last command applies only to implemented live paths; use the portal guide for portal-led labs.
Do not interpret an offline fixture, contract preview or local rule as a live AI result.

## Expected result and checkpoint

Stable source names, content hashes and chunk IDs. Cloud success is an indexer run with visible enriched fields.

Save one successful result and one failure example. Record the lab ID, model/service version,
settings changed and what you learned in [PROGRESS.csv](../../PROGRESS.csv).
You are ready to continue when you can identify the input, trust boundary, output and failure behavior.

## Experiment

Edit a source and compare its hash. Delete it and plan removal of stale index documents. Upload the synthetic receipt image to Blob Storage and inspect OCR enrichment in the portal.

## Explain before proceeding

Why does this design fit the requirement? What failure would you expect if one control were removed?
Give a 60-second answer before reading [INSTRUCTOR_NOTES.md](INSTRUCTOR_NOTES.md).

If blocked, use [troubleshooting](../../docs/TROUBLESHOOTING.md) and report the lab ID with a
sanitized error. Remove unused learning resources using [cleanup guidance](../../docs/CLEANUP.md).

Previous: [09 Azure Search vector hybrid semantic](../09_azure_search_vector_hybrid_semantic/README.md) · Next: [11 Grounded answers with RAG](../11_grounded_answers_with_rag/README.md)

## Additional Databricks variation

Import `databricks/extensions/10_custom_enrichment.py` after this lab. Read the matching extension code and setup before using live=true.
