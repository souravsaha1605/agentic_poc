# Azure setup for lab 20

Follow [docs/setup/07_APPROVALS_LOGIC_APPS.md](../../docs/setup/07_APPROVALS_LOGIC_APPS.md) in order, then return to [README.md](README.md).
For Databricks secrets/authentication use [DATABRICKS.md](../../docs/setup/DATABRICKS.md).

Before live execution verify:

- Resource is in the intended learning subscription/group and supported region.
- The endpoint belongs to the intended API family and deployment/analyzer name exists.
- The actual notebook/service identity has the required data permissions.
- Secret scope keys match `databricks/secret_mapping.json` for this lab.
- Network connectivity and private DNS, when applicable, are tested from the actual driver.

variant=reject demonstrates the rejection path. Cloud Logic Apps work follows PORTAL.md.

Completion evidence: Pending → approved → executed, or pending → rejected. No external transaction occurs.
