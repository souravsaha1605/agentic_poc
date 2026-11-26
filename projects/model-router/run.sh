#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [[ $# != 1 || $1 != --live ]]; then
    echo 'Usage: ./run.sh --live (requires Azure configuration)' >&2
    exit 2
fi
for name in AZURE_AI_PROJECT_ENDPOINT MODEL_DEPLOYMENT_NAME; do
    if [[ -z ${!name:-} ]]; then
        echo "Missing environment variable: $name" >&2
        exit 2
    fi
done
cd source
python3 -m venv .venv
.venv/bin/python -m pip install --disable-pip-version-check --no-input -r requirements.txt
exec .venv/bin/python model-router-foundry-responses.py
