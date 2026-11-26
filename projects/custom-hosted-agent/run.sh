#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [[ $# != 1 || $1 != --live ]]; then
    echo 'Usage: ./run.sh --live (requires Azure configuration)' >&2
    exit 2
fi
for name in FOUNDRY_PROJECT_ENDPOINT AZURE_AI_MODEL_DEPLOYMENT_NAME; do
    if [[ -z ${!name:-} ]]; then
        echo "Missing environment variable: $name" >&2
        exit 2
    fi
done
if curl --noproxy '*' --silent --max-time 1 http://127.0.0.1:8088/ >/dev/null; then
    echo 'Port 8088 already has an HTTP listener.' >&2
    exit 2
fi
command -v uv >/dev/null || { echo 'Install uv first.' >&2; exit 2; }
cd source/src/hello-world-python-responses
uv sync --frozen --python 3.12
.venv/bin/python main.py &
server=$!
trap 'kill "$server" 2>/dev/null || true; wait "$server" 2>/dev/null || true' EXIT
for ((attempt=0; attempt<60; attempt++)); do
    kill -0 "$server" || { echo 'Agent host exited before startup.' >&2; exit 1; }
    if curl --noproxy '*' --silent --max-time 1 http://127.0.0.1:8088/ >/dev/null; then
        curl --noproxy '*' --fail-with-body --silent --show-error --max-time 120 \
            http://127.0.0.1:8088/responses -H 'Content-Type: application/json' \
            -d '{"input":"How can you help me?","stream":false}'
        exit
    fi
    sleep 1
done
echo 'Agent host did not listen on port 8088.' >&2
exit 1
