#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
mode=()
if [[ $# == 1 && $1 == --live ]]; then
    mode=(--live)
elif [[ $# != 0 ]]; then
    echo 'Usage: ./run.sh [--live]' >&2
    exit 2
fi
if [[ ${#mode[@]} == 1 ]]; then
    for name in FOUNDRY_PROJECT_ENDPOINT FOUNDRY_MODEL_NAME; do
        if [[ -z ${!name:-} ]]; then
            echo "Missing environment variable: $name" >&2
            exit 2
        fi
    done
fi
cd source
python3 -m venv .venv
.venv/bin/python -m pip install --disable-pip-version-check --no-input -r requirements.txt
exec .venv/bin/python main.py "${mode[@]}"
