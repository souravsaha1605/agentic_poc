# Run manually

From the project folder, authenticate with Azure CLI and export FOUNDRY_PROJECT_ENDPOINT, AZURE_AI_MODEL_DEPLOYMENT_NAME. Use an existing Foundry project and model deployment. For toolbox access, follow the connection steps in the upstream README before exporting its endpoint.

In terminal one:

```bash
cd source/src/hello-world-python-responses
uv sync --frozen --python 3.12
uv run --no-sync python main.py
```

In terminal two:

```bash
curl --fail-with-body --silent --show-error http://127.0.0.1:8088/responses \
  -H 'Content-Type: application/json' \
  -d '{"input":"How can you help me?","stream":false}'
```

For hosted deployment or optimization, follow [the upstream README](source/README.md) and review the Azure resources before provisioning.

Expected result · A model-backed answer through the custom Responses adapter.

For automation use `./run.sh --live`. This uses existing Azure resources and can incur usage charges. Treat outputs as model-generated. Review [troubleshooting](../../guides/foundry-troubleshooting.md) if the call fails.
