#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [[ $# != 1 || $1 != --live ]]; then
    echo 'Usage: ./run.sh --live (requires Azure configuration)' >&2
    exit 2
fi
for name in FOUNDRY_PROJECT_ENDPOINT FOUNDRY_MODEL_NAME SHAREPOINT_CONNECTION_ID MCP_SERVER_URL; do
    if [[ -z ${!name:-} ]]; then
        echo "Missing environment variable: $name" >&2
        exit 2
    fi
done
cd source
python3 -m venv .venv
.venv/bin/python -m pip install --disable-pip-version-check --no-input -r requirements.txt
exec .venv/bin/python main.py
