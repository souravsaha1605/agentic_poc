# Run manually

Use a disposable Foundry development project with a model deployment, evaluation storage connection and appropriate project permissions. For the trace example, connect Application Insights before running. Sign in with `az login` and export `FOUNDRY_PROJECT_ENDPOINT` and `FOUNDRY_MODEL_NAME`.

```bash
cd source
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
export FOUNDRY_AGENT_NAME="portfolio-eval-$(python3 -c 'import uuid; print(uuid.uuid4().hex[:10])')"
.venv/bin/python sample_dataset_generation_job_traces_for_evaluation.py
```

The sample prints job or evaluation output. It may take several minutes and use billable services. Some samples remove their temporary resources on completion. The automated equivalent is `./run.sh --live`.
