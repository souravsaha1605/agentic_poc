# Azure setup for lab 09

Follow [docs/setup/05_SEARCH_AND_INGESTION.md](../../docs/setup/05_SEARCH_AND_INGESTION.md) in order, then return to [README.md](README.md).
For Databricks secrets/authentication use [DATABRICKS.md](../../docs/setup/DATABRICKS.md).

Before live execution verify:

- Resource is in the intended learning subscription/group and supported region.
- The endpoint belongs to the intended API family and deployment/analyzer name exists.
- The actual notebook/service identity has the required data permissions.
- Secret scope keys match `databricks/secret_mapping.json` for this lab.
- Network connectivity and private DNS, when applicable, are tested from the actual driver.

For initial cloud ingestion use variant=ingest, then variant=default to query.

Completion evidence: Ingest writes five synthetic records; query mode compares four search methods. Private partner evidence is filtered out.
