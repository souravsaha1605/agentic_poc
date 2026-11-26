# Run manually

Sign in with `az login` and export `FOUNDRY_PROJECT_ENDPOINT` and `FOUNDRY_MODEL_NAME` for a supported development deployment. Live inference can incur usage charges.

```bash
cd source
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py --live
```

Run `./run.sh` for the offline validation of the example. The live run prints the validated model-produced event. Use `./run.sh --live` for the automated equivalent.
