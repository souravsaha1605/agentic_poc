# Azure setup for lab 31

Follow [docs/setup/11_DEPLOYMENT_AND_NETWORKING.md](../../docs/setup/11_DEPLOYMENT_AND_NETWORKING.md) in order, then return to [README.md](README.md).
For Databricks secrets/authentication use [DATABRICKS.md](../../docs/setup/DATABRICKS.md).

Before live execution verify:

- Resource is in the intended learning subscription/group and supported region.
- The endpoint belongs to the intended API family and deployment/analyzer name exists.
- The actual notebook/service identity has the required data permissions.
- Secret scope keys match `databricks/secret_mapping.json` for this lab.
- Network connectivity and private DNS, when applicable, are tested from the actual driver.

The script is an artifact check; follow PORTAL.md for actual deployment commands.

Completion evidence: All infrastructure and deployment files exist. Cloud deployment is an explicit guided workflow.
