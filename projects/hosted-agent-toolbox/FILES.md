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
| [source/src/agent-framework-agent-with-foundry-toolbox-responses/.azdignore](source/src/agent-framework-agent-with-foundry-toolbox-responses/.azdignore) | Excludes local files from azd packaging. |
| [source/src/agent-framework-agent-with-foundry-toolbox-responses/.dockerignore](source/src/agent-framework-agent-with-foundry-toolbox-responses/.dockerignore) | Excludes files from the Docker build context. |
| [source/src/agent-framework-agent-with-foundry-toolbox-responses/.env.example](source/src/agent-framework-agent-with-foundry-toolbox-responses/.env.example) | Documents required settings without secrets. |
| [source/src/agent-framework-agent-with-foundry-toolbox-responses/Dockerfile](source/src/agent-framework-agent-with-foundry-toolbox-responses/Dockerfile) | Builds the hosted agent container image. |
| [source/src/agent-framework-agent-with-foundry-toolbox-responses/main.py](source/src/agent-framework-agent-with-foundry-toolbox-responses/main.py) | Expose tools through a single MCP endpoint and connect the hosted agent to that toolbox. |
| [source/src/agent-framework-agent-with-foundry-toolbox-responses/pyproject.toml](source/src/agent-framework-agent-with-foundry-toolbox-responses/pyproject.toml) | Lists the Python project and dependency constraints. |
| [source/src/agent-framework-agent-with-foundry-toolbox-responses/scripts/list-foundry-connectors.ps1](source/src/agent-framework-agent-with-foundry-toolbox-responses/scripts/list-foundry-connectors.ps1) | PowerShell helper for listing configured connectors. |
| [source/src/agent-framework-agent-with-foundry-toolbox-responses/scripts/list-foundry-connectors.sh](source/src/agent-framework-agent-with-foundry-toolbox-responses/scripts/list-foundry-connectors.sh) | Bash helper for listing configured connectors. |
| [source/src/agent-framework-agent-with-foundry-toolbox-responses/uv.lock](source/src/agent-framework-agent-with-foundry-toolbox-responses/uv.lock) | Pins dependencies for reproducible uv sync. |
| [source/src/agent-framework-agent-with-foundry-toolbox-responses/uv.toml](source/src/agent-framework-agent-with-foundry-toolbox-responses/uv.toml) | Configures uv for this sample. |
