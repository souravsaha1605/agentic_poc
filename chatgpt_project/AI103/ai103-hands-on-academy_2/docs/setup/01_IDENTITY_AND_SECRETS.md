# Identity and secrets in Azure Portal

1. Create a dedicated resource group such as `rg-ai103-learning`. Record subscription,
   tenant, region, owner and purpose in your progress notes. Add a budget alert in Cost Management.
2. Search **Key vaults → Create**. Use a globally unique name and an approved region. For the
   direct SDK lab choose Azure RBAC under Access configuration. Keep soft delete enabled.
   For a traditional Databricks-backed Key Vault scope use the separate access-policy vault
   described in DATABRICKS.md; these are different permission models.
3. In the RBAC vault → **Access control (IAM)**, have an authorized administrator grant your
   learning principal **Key Vault Secrets Officer** only while creating test secrets.
   Create `lab-demo-secret` with a dummy value under **Objects → Secrets → Generate/Import**.
   For the runtime reader, grant **Key Vault Secrets User** at vault scope. Role propagation
   may take time. The management-plane Reader role cannot read secret values.
4. Record Vault URI in KEY_VAULT_URL and secret name in KEY_VAULT_SECRET_NAME. In Databricks,
   store the corresponding values in the configuration secret scope and use the app principal
   described in DATABRICKS.md. Locally use Azure CLI login or the same explicit app identity.
5. Run lab 01 live. Inspect only secret name/version and found=true. Rotate the dummy secret,
   rerun, and observe the version changing without a code change.
6. For an Azure-hosted application, open its **Identity** page, enable a system-assigned managed
   identity, save, and assign that principal the required data role on the target service.
   Do not assume a developer's role assignments are inherited by the deployed identity.
7. Test denial by using a learning principal without the data role. Distinguish 401 identity
   problems, 403 authorization problems and network/DNS failures. Keep request IDs, not tokens.

Authentication answers who; authorization answers what; auditing answers who did what and why.
Record user invocation separately from the agent's tool action. Assign an accountable human
owner to each workload identity. For CI, prefer workload federation to long-lived client secrets.

Reference: https://learn.microsoft.com/en-us/azure/key-vault/secrets/quick-create-python
