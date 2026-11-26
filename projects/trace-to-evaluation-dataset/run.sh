#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/source"
if [[ $# != 1 || $1 != --live ]]; then
    echo 'Usage: ./run.sh --live (requires a disposable Foundry project)' >&2
    exit 2
fi
for name in FOUNDRY_PROJECT_ENDPOINT FOUNDRY_MODEL_NAME; do
    if [[ -z ${!name:-} ]]; then
        echo "Missing environment variable: $name" >&2
        exit 2
    fi
done
export FOUNDRY_AGENT_NAME="portfolio-eval-$(python3 -c 'import uuid; print(uuid.uuid4().hex[:10])')"
python3 -m venv .venv
.venv/bin/python -m pip install --disable-pip-version-check --no-input -r requirements.txt
exec .venv/bin/python sample_dataset_generation_job_traces_for_evaluation.py
