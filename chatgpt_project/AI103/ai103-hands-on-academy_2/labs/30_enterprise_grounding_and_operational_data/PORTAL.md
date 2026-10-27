# Azure setup for lab 30

Follow [docs/setup/06_MEMORY_AND_ENTERPRISE.md](../../docs/setup/06_MEMORY_AND_ENTERPRISE.md) in order, then return to [README.md](README.md).
For Databricks secrets/authentication use [DATABRICKS.md](../../docs/setup/DATABRICKS.md).

Before live execution verify:

- Resource is in the intended learning subscription/group and supported region.
- The endpoint belongs to the intended API family and deployment/analyzer name exists.
- The actual notebook/service identity has the required data permissions.
- Secret scope keys match `databricks/secret_mapping.json` for this lab.
- Network connectivity and private DNS, when applicable, are tested from the actual driver.

variant=fabric runs the parameterized SQL read; see cosmos_vector.py for the separate vector extension.

Completion evidence: Local two-source join or a parameterized read from your Fabric SQL analytics endpoint.
