# Azure setup for lab 21

Follow [docs/setup/08_MCP.md](../../docs/setup/08_MCP.md) in order, then return to [README.md](README.md).
For Databricks secrets/authentication use [DATABRICKS.md](../../docs/setup/DATABRICKS.md).

Before live execution verify:

- Resource is in the intended learning subscription/group and supported region.
- The endpoint belongs to the intended API family and deployment/analyzer name exists.
- The actual notebook/service identity has the required data permissions.
- Secret scope keys match `databricks/secret_mapping.json` for this lab.
- Network connectivity and private DNS, when applicable, are tested from the actual driver.

live=true means a real local MCP protocol run here; it does not call Azure.

Completion evidence: Protocol discovery exposes public_policy and invocation returns policy evidence. --live here means real local MCP transport, not Azure.
