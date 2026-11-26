# File guide

| File | What it does and why it matters |
| --- | --- |
| README.md | Describes the scenario, services, attribution, and expected result. |
| SOURCE-STEPS.md | Records the original walkthrough sequence for reference. |
| RUN-MANUALLY.md | Explains how to reproduce the sample and inspect its output. |
| run.sh | Checks settings, then launches the sample and returns its result. |
| [source/LICENSE](source/LICENSE) | Preserves the license and copyright of the copied upstream code. |
| [source/README.md](source/README.md) | Upstream setup and architecture notes. |
| [source/azure.yaml](source/azure.yaml) | azd definition for deploying the Azure services. |
| [source/src/agent-framework-agent-basic-responses/.azdignore](source/src/agent-framework-agent-basic-responses/.azdignore) | Excludes local files from azd packaging. |
| [source/src/agent-framework-agent-basic-responses/.dockerignore](source/src/agent-framework-agent-basic-responses/.dockerignore) | Excludes files from the Docker build context. |
| [source/src/agent-framework-agent-basic-responses/.env.example](source/src/agent-framework-agent-basic-responses/.env.example) | Documents required settings without secrets. |
| [source/src/agent-framework-agent-basic-responses/Dockerfile](source/src/agent-framework-agent-basic-responses/Dockerfile) | Builds the hosted agent container image. |
| [source/src/agent-framework-agent-basic-responses/main.py](source/src/agent-framework-agent-basic-responses/main.py) | Package a Python Agent Framework agent, start the Responses host, and invoke it. |
| [source/src/agent-framework-agent-basic-responses/pyproject.toml](source/src/agent-framework-agent-basic-responses/pyproject.toml) | Lists the Python project and dependency constraints. |
| [source/src/agent-framework-agent-basic-responses/uv.lock](source/src/agent-framework-agent-basic-responses/uv.lock) | Pins dependencies for reproducible uv sync. |
| [source/src/agent-framework-agent-basic-responses/uv.toml](source/src/agent-framework-agent-basic-responses/uv.toml) | Configures uv for this sample. |
