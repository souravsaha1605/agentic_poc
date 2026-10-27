# Azure setup for lab 01

Follow [docs/setup/01_IDENTITY_AND_SECRETS.md](../../docs/setup/01_IDENTITY_AND_SECRETS.md) in order, then return to [README.md](README.md).
For Databricks secrets/authentication use [DATABRICKS.md](../../docs/setup/DATABRICKS.md).

Before live execution verify:

- Resource is in the intended learning subscription/group and supported region.
- The endpoint belongs to the intended API family and deployment/analyzer name exists.
- The actual notebook/service identity has the required data permissions.
- Secret scope keys match `databricks/secret_mapping.json` for this lab.
- Network connectivity and private DNS, when applicable, are tested from the actual driver.

Use variant=default initially.

Completion evidence: A secret name/version and found=true; the secret value is never printed.
