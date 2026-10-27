# Azure setup for lab 15

Follow [docs/setup/06_MEMORY_AND_ENTERPRISE.md](../../docs/setup/06_MEMORY_AND_ENTERPRISE.md) in order, then return to [README.md](README.md).
For Databricks secrets/authentication use [DATABRICKS.md](../../docs/setup/DATABRICKS.md).

Before live execution verify:

- Resource is in the intended learning subscription/group and supported region.
- The endpoint belongs to the intended API family and deployment/analyzer name exists.
- The actual notebook/service identity has the required data permissions.
- Secret scope keys match `databricks/secret_mapping.json` for this lab.
- Network connectivity and private DNS, when applicable, are tested from the actual driver.

For cloud storage choose variant=redis or variant=cosmos. Other variants are rejected.

Completion evidence: Alice sees her session; Bob sees an empty list. Live examples create and remove synthetic records.
