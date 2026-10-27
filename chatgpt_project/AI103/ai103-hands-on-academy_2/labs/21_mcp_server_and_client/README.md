# Lab 21 — MCP server and client

**Reviewed execution instructions:** start with [RUNBOOK.md](RUNBOOK.md). It lists exact widgets, secrets, variants and failure recovery.

**Prerequisites:** 12,13. **Execution:** local protocol. **Handbook sections:** 15.
Allow roughly 30–90 minutes plus resource provisioning. Stop after the acceptance check before adding the extension.

## Understand the concept

MCP standardizes discovery and invocation. The provider still owns authorization, validation and audit. The local transport avoids deploying a public server for the first exercise.

## Set up once

Read [the setup guide](../../docs/setup/08_MCP.md) and [the Databricks guide](../../docs/setup/DATABRICKS.md).
Provision only the current service. The [source script](run.py) shows the exact imports, input and result.
Optional live dependencies are in `requirements/mcp.txt`; the Databricks notebook installs that set.
Cloud examples require your own resources and permissions. They have not been executed against your subscription.

## Execute in Databricks

1. Complete bootstrap and attach the compute described in the Databricks guide.
2. Import `databricks/labs/21_mcp_server_and_client.py` as a source notebook into Workspace.
3. Set project_root and a writable volume output_root. Keep live=false and run the lesson.
4. Inspect the printed JSON and its file in output_root. Read the called function in src/academy.
5. For the Azure/protocol path, finish setup, create the per-lab secrets, set live=true, install
   the lesson packages, restart Python, and run the final cell again. Portal-led/local-only labs
   state explicitly when --live is not an Azure implementation.
6. live=true means a real local MCP protocol run here; it does not call Azure.

## Optional local commands

From the course root after the workstation setup:

```bash
python labs/21_mcp_server_and_client/run.py
python -m pip install -r requirements/mcp.txt
python labs/21_mcp_server_and_client/run.py --live
```

The last command applies only to implemented live paths; use the portal guide for portal-led labs.
Do not interpret an offline fixture, contract preview or local rule as a live AI result.

## Expected result and checkpoint

Protocol discovery exposes public_policy and invocation returns policy evidence. --live here means real local MCP transport, not Azure.

Save one successful result and one failure example. Record the lab ID, model/service version,
settings changed and what you learned in [PROGRESS.csv](../../PROGRESS.csv).
You are ready to continue when you can identify the input, trust boundary, output and failure behavior.

## Experiment

Add one read-only tool with a typed argument. Send an invalid type. Explain how authentication changes if this server is exposed over HTTP. Review v1 versus v2 migration notes before upgrading.

## Explain before proceeding

Why does this design fit the requirement? What failure would you expect if one control were removed?
Give a 60-second answer before reading [INSTRUCTOR_NOTES.md](INSTRUCTOR_NOTES.md).

If blocked, use [troubleshooting](../../docs/TROUBLESHOOTING.md) and report the lab ID with a
sanitized error. Remove unused learning resources using [cleanup guidance](../../docs/CLEANUP.md).

Previous: [20 Human approvals and Logic Apps](../20_human_approvals_and_logic_apps/README.md) · Next: [22 Tracing and loop diagnostics](../22_tracing_and_loop_diagnostics/README.md)
