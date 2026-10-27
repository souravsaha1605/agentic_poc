# Stop charges and retain useful evidence

Save sanitized result files and your progress notes first. Terminate Databricks compute when
finished; auto-termination is a backstop. Notebook library installation and driver files are
session-scoped. Keep only needed synthetic evidence in the volume.

Review the learning resource group inventory. Delete unused image/video jobs or deployments,
managed agent versions, custom Speech endpoints, search indexes/services, cache instances,
Cosmos/Fabric capacity, App Service plan and monitoring resources according to their service
lifecycle. Stopping a web app does not necessarily stop its plan charges. Model deployments and
provisioned capacity can have different billing behavior; check the selected option.

Delete only dedicated lab resources after confirming no shared workloads depend on them.
Revoke temporary role assignments and expire/delete learning client secrets. Remove test secrets
and scope access. Key Vault soft-deleted names can remain reserved; plan before recreating.
No cleanup script in this course automatically deletes a resource group.
