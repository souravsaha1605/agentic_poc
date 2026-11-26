# Run manually

Sign in with `az login` and export `FOUNDRY_PROJECT_ENDPOINT` and `FOUNDRY_MODEL_NAME` for a supported development deployment. Live inference can incur usage charges.

```bash
cd source
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python tools/sample_agent_file_search_in_stream.py
```

Use a disposable project for the upstream sample, which creates a vector store and agent version and removes them at the end. Expect streamed answers and file citations. Use `./run.sh --live` for the automated equivalent.
