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
| [source/src/hello-world-python-responses/.azdignore](source/src/hello-world-python-responses/.azdignore) | Excludes local files from azd packaging. |
| [source/src/hello-world-python-responses/.dockerignore](source/src/hello-world-python-responses/.dockerignore) | Excludes files from the Docker build context. |
| [source/src/hello-world-python-responses/.env.example](source/src/hello-world-python-responses/.env.example) | Documents required settings without secrets. |
| [source/src/hello-world-python-responses/Dockerfile](source/src/hello-world-python-responses/Dockerfile) | Builds the hosted agent container image. |
| [source/src/hello-world-python-responses/main.py](source/src/hello-world-python-responses/main.py) | Wrap application code in the Foundry Responses hosting library. |
| [source/src/hello-world-python-responses/pyproject.toml](source/src/hello-world-python-responses/pyproject.toml) | Lists the Python project and dependency constraints. |
| [source/src/hello-world-python-responses/uv.lock](source/src/hello-world-python-responses/uv.lock) | Pins dependencies for reproducible uv sync. |
| [source/src/hello-world-python-responses/uv.toml](source/src/hello-world-python-responses/uv.toml) | Configures uv for this sample. |
