# Run manually

From the project folder, use Python 3.12, configure AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, MODEL_DEPLOYMENT_NAME, and authenticate with Azure CLI for Entra-based samples. For embedding search use a deployment of an embedding model and an Azure OpenAI credential.

```bash
cd source
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py --live
```

For a credential-free run, execute `python3 source/main.py` from the project folder.

Expected result · Ranked document scores. The offline runner validates ranking with fixed illustrative vectors; live uses real model embeddings.

For automation use `./run.sh --live`. This uses existing Azure resources and can incur usage charges. Treat outputs as model-generated. Review [troubleshooting](../../guides/foundry-troubleshooting.md) if the call fails.
