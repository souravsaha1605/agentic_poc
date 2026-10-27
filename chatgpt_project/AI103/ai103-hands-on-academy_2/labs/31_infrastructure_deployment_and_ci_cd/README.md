# Lab 31 — Infrastructure deployment and CI CD

**Reviewed execution instructions:** start with [RUNBOOK.md](RUNBOOK.md). It lists exact widgets, secrets, variants and failure recovery.

**Prerequisites:** 01,16,22,23. **Execution:** local + portal/CLI. **Handbook sections:** 23,24.5.
Allow roughly 30–90 minutes plus resource provisioning. Stop after the acceptance check before adding the extension.

## Understand the concept

Version code, prompts, schemas, evaluations and infrastructure together. Deployment success and application quality are separate gates.

## Set up once

Read [the setup guide](../../docs/setup/11_DEPLOYMENT_AND_NETWORKING.md) and [the Databricks guide](../../docs/setup/DATABRICKS.md).
Provision only the current service. The [source script](run.py) shows the exact imports, input and result.
Optional live dependencies are in `requirements/core.txt`; the Databricks notebook installs that set.
Cloud examples require your own resources and permissions. They have not been executed against your subscription.

## Execute in Databricks

1. Complete bootstrap and attach the compute described in the Databricks guide.
2. Import `databricks/labs/31_infrastructure_deployment_and_ci_cd.py` as a source notebook into Workspace.
3. Set project_root and a writable volume output_root. Keep live=false and run the lesson.
4. Inspect the printed JSON and its file in output_root. Read the called function in src/academy.
5. Keep live=false for this local lesson. If it has a separate portal exercise, follow RUNBOOK.md and azure_execution; this script does not implement a live Azure branch.
6. The script is an artifact check; follow PORTAL.md for actual deployment commands.

## Optional local commands

From the course root after the workstation setup:

```bash
python labs/31_infrastructure_deployment_and_ci_cd/run.py
```

The last command applies only to implemented live paths; use the portal guide for portal-led labs.
Do not interpret an offline fixture, contract preview or local rule as a live AI result.

## Expected result and checkpoint

All infrastructure and deployment files exist. Cloud deployment is an explicit guided workflow.

Save one successful result and one failure example. Record the lab ID, model/service version,
settings changed and what you learned in [PROGRESS.csv](../../PROGRESS.csv).
You are ready to continue when you can identify the input, trust boundary, output and failure behavior.

## Experiment

Run the evaluation gate before changing prompts. Inspect a Bicep what-if result. Revoke an identity permission and test the deployed failure. Record a rollback procedure.

## Explain before proceeding

Why does this design fit the requirement? What failure would you expect if one control were removed?
Give a 60-second answer before reading [INSTRUCTOR_NOTES.md](INSTRUCTOR_NOTES.md).

If blocked, use [troubleshooting](../../docs/TROUBLESHOOTING.md) and report the lab ID with a
sanitized error. Remove unused learning resources using [cleanup guidance](../../docs/CLEANUP.md).

Previous: [30 Enterprise grounding and operational data](../30_enterprise_grounding_and_operational_data/README.md) · Next: [32 Cost quotas scaling and drift](../32_cost_quotas_scaling_and_drift/README.md)
