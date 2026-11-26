# Run manually

From the project folder, use Python 3.12, configure FOUNDRY_PROJECT_ENDPOINT, FOUNDRY_MODEL_NAME, and authenticate with Azure CLI for Entra-based samples.

```bash
cd source
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

Expected result · A short answer from the configured deployment.

For automation use `./run.sh --live`. This uses existing Azure resources and can incur usage charges. Treat outputs as model-generated. Review [troubleshooting](../../guides/foundry-troubleshooting.md) if the call fails.
