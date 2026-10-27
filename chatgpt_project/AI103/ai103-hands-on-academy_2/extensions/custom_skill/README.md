# Custom enrichment skill

**Reviewed execution instructions:** start with [RUNBOOK.md](RUNBOOK.md). It lists exact widgets, secrets, variants and failure recovery.

Run `python extensions/custom_skill/handler.py` locally or use runpy from a Databricks notebook.
Inspect the values/recordId/data/errors/warnings contract. Import `enrich` into an authenticated
HTTP Azure Function or approved API endpoint, and map the template URI to that endpoint in
an Azure Search skillset. The template is not deployable until you supply the host and supported
authentication configuration. Test malformed records and partial failures before indexing.
