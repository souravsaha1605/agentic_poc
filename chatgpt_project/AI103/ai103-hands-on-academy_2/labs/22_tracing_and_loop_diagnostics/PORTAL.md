# Azure setup for lab 22

Follow [docs/setup/09_MONITORING.md](../../docs/setup/09_MONITORING.md) in order, then return to [README.md](README.md).
For Databricks secrets/authentication use [DATABRICKS.md](../../docs/setup/DATABRICKS.md).

Before live execution verify:

- Resource is in the intended learning subscription/group and supported region.
- The endpoint belongs to the intended API family and deployment/analyzer name exists.
- The actual notebook/service identity has the required data permissions.
- Secret scope keys match `databricks/secret_mapping.json` for this lab.
- Network connectivity and private DNS, when applicable, are tested from the actual driver.

Use variant=default initially.

Completion evidence: A parent and child span appear in Application Insights in live mode; no prompt content is attached.
