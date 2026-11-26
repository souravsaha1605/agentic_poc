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
| [source/src/optimization-customer-support-python-responses/.agent_configs/baseline/instructions.md](source/src/optimization-customer-support-python-responses/.agent_configs/baseline/instructions.md) | Baseline agent instructions. |
| [source/src/optimization-customer-support-python-responses/.agent_configs/baseline/metadata.yaml](source/src/optimization-customer-support-python-responses/.agent_configs/baseline/metadata.yaml) | Metadata for the baseline optimization candidate. |
| [source/src/optimization-customer-support-python-responses/.azdignore](source/src/optimization-customer-support-python-responses/.azdignore) | Excludes local files from azd packaging. |
| [source/src/optimization-customer-support-python-responses/.dockerignore](source/src/optimization-customer-support-python-responses/.dockerignore) | Excludes files from the Docker build context. |
| [source/src/optimization-customer-support-python-responses/.env.example](source/src/optimization-customer-support-python-responses/.env.example) | Documents required settings without secrets. |
| [source/src/optimization-customer-support-python-responses/Dockerfile](source/src/optimization-customer-support-python-responses/Dockerfile) | Builds the hosted agent container image. |
| [source/src/optimization-customer-support-python-responses/eval-quick.jsonl](source/src/optimization-customer-support-python-responses/eval-quick.jsonl) | A smaller set of evaluation cases. |
| [source/src/optimization-customer-support-python-responses/eval.jsonl](source/src/optimization-customer-support-python-responses/eval.jsonl) | Evaluation cases for comparative scoring. |
| [source/src/optimization-customer-support-python-responses/eval.yaml](source/src/optimization-customer-support-python-responses/eval.yaml) | Defines evaluation inputs and configuration. |
| [source/src/optimization-customer-support-python-responses/main.py](source/src/optimization-customer-support-python-responses/main.py) | Use representative customer queries and evaluation criteria to compare instruction candidates. |
| [source/src/optimization-customer-support-python-responses/pyproject.toml](source/src/optimization-customer-support-python-responses/pyproject.toml) | Lists the Python project and dependency constraints. |
| [source/src/optimization-customer-support-python-responses/skills/escalation/SKILL.md](source/src/optimization-customer-support-python-responses/skills/escalation/SKILL.md) | Sample runtime guidance consumed by the support agent. |
| [source/src/optimization-customer-support-python-responses/skills/handle-return/SKILL.md](source/src/optimization-customer-support-python-responses/skills/handle-return/SKILL.md) | Sample runtime guidance consumed by the support agent. |
| [source/src/optimization-customer-support-python-responses/skills/safety-boundaries/SKILL.md](source/src/optimization-customer-support-python-responses/skills/safety-boundaries/SKILL.md) | Sample runtime guidance consumed by the support agent. |
| [source/src/optimization-customer-support-python-responses/skills/troubleshoot-device/SKILL.md](source/src/optimization-customer-support-python-responses/skills/troubleshoot-device/SKILL.md) | Sample runtime guidance consumed by the support agent. |
| [source/src/optimization-customer-support-python-responses/uv.lock](source/src/optimization-customer-support-python-responses/uv.lock) | Pins dependencies for reproducible uv sync. |
| [source/src/optimization-customer-support-python-responses/uv.toml](source/src/optimization-customer-support-python-responses/uv.toml) | Configures uv for this sample. |
