# Optional local workstation

The primary route is DATABRICKS.md. For local execution install Python 3.11+, VS Code and
Azure CLI using the official installers. Extract the ZIP and open its root folder in VS Code.

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
Copy-Item .env.example .env
python labs/00_environment_and_project_tour/run.py
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
cp .env.example .env
python labs/00_environment_and_project_tour/run.py
```

If PowerShell activation is restricted, use `.venv\Scripts\python.exe` directly instead
of changing machine-wide execution policy. Run commands from the course root.
Install only the requirement file named by the current lesson, for example
`python -m pip install -r requirements/core.txt`. Cloud SDKs are imported only on live paths.
Use `.env` locally; Databricks uses secret scopes. The process environment takes precedence.
For Entra SDK exercises, local `az login` can provide developer credentials. Select the
intended subscription with `az account set --subscription <id>`.

In VS Code select the virtual environment interpreter, put a breakpoint at the first provider
call, and inspect request fields WITHOUT expanding credentials. To reset a lab, remove only
its output files; avoid deleting the whole course or resource group until you have checked scope.
