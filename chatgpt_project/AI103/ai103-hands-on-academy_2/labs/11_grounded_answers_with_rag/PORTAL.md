# Azure setup for lab 11

Follow [docs/setup/05_SEARCH_AND_INGESTION.md](../../docs/setup/05_SEARCH_AND_INGESTION.md) in order, then return to [README.md](README.md).
For Databricks secrets/authentication use [DATABRICKS.md](../../docs/setup/DATABRICKS.md).

Before live execution verify:

- Resource is in the intended learning subscription/group and supported region.
- The endpoint belongs to the intended API family and deployment/analyzer name exists.
- The actual notebook/service identity has the required data permissions.
- Secret scope keys match `databricks/secret_mapping.json` for this lab.
- Network connectivity and private DNS, when applicable, are tested from the actual driver.

Use variant=default initially.

Completion evidence: An answer and source IDs, or explicit insufficient evidence. Live mode uses Azure Search, model, moderation and Prompt Shields.
