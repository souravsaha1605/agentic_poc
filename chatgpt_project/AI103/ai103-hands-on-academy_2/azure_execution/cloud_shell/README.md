# Run Azure administration in Cloud Shell

1. In Azure Portal verify the directory/subscription selector is your learning subscription.
2. Select `>_` (Cloud Shell), select **Bash**, and complete its storage prompt if required.
3. Use **Manage files → Upload** to upload the course ZIP. Run `ls` to check its name.
4. Extract it and enter its folder:

```bash
unzip -o ai103-hands-on-academy.zip
cd ai103-hands-on-academy
az account show --query '{subscription:name,tenant:tenantId}' -o table
python3 --version
```

For infrastructure follow [infra/README.md](../../infra/README.md). Replace angle-bracket
placeholders before executing commands. Never put secrets in command arguments or shell history.
`az bicep build --file infra/main.bicep` must succeed before `what-if` or deployment.
Cloud Shell might need to download Bicep; if policy blocks downloads ask the subscription admin
for the supported deployment route. A source template is not proof that it has compiled.

For Cosmos data roles use the command in [memory setup](../../docs/setup/06_MEMORY_AND_ENTERPRISE.md).
`principal-object-id` is **Enterprise applications → your app → Object ID**, not the application
(client) ID or the app-registration object's Object ID. Recheck that the scope is your learning database.

Cloud Shell is an administration terminal, not a durable application server or native Speech host.
