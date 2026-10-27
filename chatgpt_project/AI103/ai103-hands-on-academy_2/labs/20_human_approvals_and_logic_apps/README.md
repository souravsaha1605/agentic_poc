# Lab 20 — Human approvals and Logic Apps

**Reviewed execution instructions:** start with [RUNBOOK.md](RUNBOOK.md). It lists exact widgets, secrets, variants and failure recovery.

**Prerequisites:** 13,14. **Execution:** local + portal. **Handbook sections:** 17.
Allow roughly 30–90 minutes plus resource provisioning. Stop after the acceptance check before adding the extension.

## Understand the concept

Approval is durable workflow state, separate from an HTTP timeout. A decision is bound to request payload, approver identity and expiry.

## Set up once

Read [the setup guide](../../docs/setup/07_APPROVALS_LOGIC_APPS.md) and [the Databricks guide](../../docs/setup/DATABRICKS.md).
Provision only the current service. The [source script](run.py) shows the exact imports, input and result.
Optional live dependencies are in `requirements/core.txt`; the Databricks notebook installs that set.
Cloud examples require your own resources and permissions. They have not been executed against your subscription.

## Execute in Databricks

1. Complete bootstrap and attach the compute described in the Databricks guide.
2. Import `databricks/labs/20_human_approvals_and_logic_apps.py` as a source notebook into Workspace.
3. Set project_root and a writable volume output_root. Keep live=false and run the lesson.
4. Inspect the printed JSON and its file in output_root. Read the called function in src/academy.
5. Keep live=false for this local lesson. If it has a separate portal exercise, follow RUNBOOK.md and azure_execution; this script does not implement a live Azure branch.
6. variant=reject demonstrates the rejection path. Cloud Logic Apps work follows PORTAL.md.

## Optional local commands

From the course root after the workstation setup:

```bash
python labs/20_human_approvals_and_logic_apps/run.py
```

The last command applies only to implemented live paths; use the portal guide for portal-led labs.
Do not interpret an offline fixture, contract preview or local rule as a live AI result.

## Expected result and checkpoint

Pending → approved → executed, or pending → rejected. No external transaction occurs.

Save one successful result and one failure example. Record the lab ID, model/service version,
settings changed and what you learned in [PROGRESS.csv](../../PROGRESS.csv).
You are ready to continue when you can identify the input, trust boundary, output and failure behavior.

## Experiment

Run --variant reject. Expire a request. Attempt self-approval and non-supervisor approval. Follow the portal guide to persist requests and decisions asynchronously.

## Explain before proceeding

Why does this design fit the requirement? What failure would you expect if one control were removed?
Give a 60-second answer before reading [INSTRUCTOR_NOTES.md](INSTRUCTOR_NOTES.md).

If blocked, use [troubleshooting](../../docs/TROUBLESHOOTING.md) and report the lab ID with a
sanitized error. Remove unused learning resources using [cleanup guidance](../../docs/CLEANUP.md).

Previous: [19 Multi agent orchestration and reflection](../19_multi_agent_orchestration_and_reflection/README.md) · Next: [21 MCP server and client](../21_mcp_server_and_client/README.md)

Implemented next exercise: [logic app submit](../../extensions/logic_app_submit/RUNBOOK.md).
