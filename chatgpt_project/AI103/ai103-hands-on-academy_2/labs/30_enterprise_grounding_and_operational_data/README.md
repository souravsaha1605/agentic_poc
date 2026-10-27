# Lab 30 — Enterprise grounding and operational data

**Reviewed execution instructions:** start with [RUNBOOK.md](RUNBOOK.md). It lists exact widgets, secrets, variants and failure recovery.

**Prerequisites:** 09,15. **Execution:** local + Azure. **Handbook sections:** 8.
Allow roughly 30–90 minutes plus resource provisioning. Stop after the acceptance check before adding the extension.

## Understand the concept

Use document search for policies, live records for current order state, and analytical stores for aggregated sales. Keep authorization and freshness explicit across the joins.

## Set up once

Read [the setup guide](../../docs/setup/06_MEMORY_AND_ENTERPRISE.md) and [the Databricks guide](../../docs/setup/DATABRICKS.md).
Provision only the current service. The [source script](run.py) shows the exact imports, input and result.
Optional live dependencies are in `requirements/fabric.txt`; the Databricks notebook installs that set.
Cloud examples require your own resources and permissions. They have not been executed against your subscription.

## Execute in Databricks

1. Complete bootstrap and attach the compute described in the Databricks guide.
2. Import `databricks/labs/30_enterprise_grounding_and_operational_data.py` as a source notebook into Workspace.
3. Set project_root and a writable volume output_root. Keep live=false and run the lesson.
4. Inspect the printed JSON and its file in output_root. Read the called function in src/academy.
5. For the Azure/protocol path, finish setup, create the per-lab secrets, set live=true, install
   the lesson packages, restart Python, and run the final cell again. Portal-led/local-only labs
   state explicitly when --live is not an Azure implementation.
6. variant=fabric runs the parameterized SQL read; see cosmos_vector.py for the separate vector extension.

## Optional local commands

From the course root after the workstation setup:

```bash
python labs/30_enterprise_grounding_and_operational_data/run.py
python -m pip install -r requirements/fabric.txt
python labs/30_enterprise_grounding_and_operational_data/run.py --live --variant fabric
```

The last command applies only to implemented live paths; use the portal guide for portal-led labs.
Do not interpret an offline fixture, contract preview or local rule as a live AI result.

## Expected result and checkpoint

Local two-source join or a parameterized read from your Fabric SQL analytics endpoint.

Save one successful result and one failure example. Record the lab ID, model/service version,
settings changed and what you learned in [PROGRESS.csv](../../PROGRESS.csv).
You are ready to continue when you can identify the input, trust boundary, output and failure behavior.

## Experiment

Run the Fabric/OneLake setup and SQL seed. Change inventory without changing monthly sales. Try a restricted user. Run the Cosmos vector extension after enabling vector search.

## Explain before proceeding

Why does this design fit the requirement? What failure would you expect if one control were removed?
Give a 60-second answer before reading [INSTRUCTOR_NOTES.md](INSTRUCTOR_NOTES.md).

If blocked, use [troubleshooting](../../docs/TROUBLESHOOTING.md) and report the lab ID with a
sanitized error. Remove unused learning resources using [cleanup guidance](../../docs/CLEANUP.md).

Previous: [29 Video generation and editing](../29_video_generation_and_editing/README.md) · Next: [31 Infrastructure deployment and CI CD](../31_infrastructure_deployment_and_ci_cd/README.md)

## Additional Databricks variation

Import `databricks/extensions/30_cosmos_vector.py` after this lab. Read the matching extension code and setup before using live=true.
