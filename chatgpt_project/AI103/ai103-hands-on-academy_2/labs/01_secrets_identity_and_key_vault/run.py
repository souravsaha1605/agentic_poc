# Purpose: Read a secret through a trusted identity
# Learn: Distinguish authentication, authorization, secret scope access and Key Vault data permissions.
# Run: Import databricks/labs/01_secrets_identity_and_key_vault.py as a Databricks source notebook. Start live=false; read labs/01_secrets_identity_and_key_vault/RUNBOOK.md.

"""Lab 01: Secrets identity and Key Vault. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import args,env,save
opts=args('Read a secret without printing its value')
if opts.live:
    from azure.identity import DefaultAzureCredential
    from azure.keyvault.secrets import SecretClient
    credential=DefaultAzureCredential()
    client=SecretClient(env('KEY_VAULT_URL'),credential)
    secret=client.get_secret(env('KEY_VAULT_SECRET_NAME','lab-demo-secret'))
    result={'found':secret.value is not None,'secret_name':secret.name,'version':secret.properties.version}
else:
    result={'mode':'local configuration exercise','secret_in_code':False,'next':'Create lab-demo-secret and run --live'}
save('01_identity.json',result)
