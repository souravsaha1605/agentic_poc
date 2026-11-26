# Run manually

From the project folder, use Python 3.12, configure FOUNDRY_PROJECT_ENDPOINT, FOUNDRY_MODEL_NAME, SHAREPOINT_CONNECTION_ID, MCP_SERVER_URL, and authenticate with Azure CLI for Entra-based samples.

```bash
cd source
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

After checking the answers, run `.venv/bin/python evaluate.py` from the same directory to submit the separate evaluation.

Expected result · Answers that use both sources and a separate evaluation result.

For automation use `./run.sh --live`. This uses existing Azure resources and can incur usage charges. Treat outputs as model-generated. Review [troubleshooting](../../guides/foundry-troubleshooting.md) if the call fails.

The local requirements pin Azure AI Projects 2.11.0 and include Azure Identity. Use these requirements when a version shown inside the upstream scripts differs.
