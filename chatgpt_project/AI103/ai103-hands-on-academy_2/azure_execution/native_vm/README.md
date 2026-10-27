# Azure VM fallback for native Speech, MCP and ODBC

Try the dedicated Databricks path first. Use this folder if the workspace administrator confirms
that native dependencies or subprocesses are unavailable. Do not run a public server in Cloud Shell.

1. Azure Portal → Virtual machines → Create. Use an approved Ubuntu 24.04 LTS image, a small learning VM,
   SSH key authentication, and a restricted inbound SSH rule for your own IP (or Azure Bastion).
   Record charges; configure auto-shutdown. Avoid a broad internet-open SSH rule.
2. VM → Connect → Bastion/SSH. Use the portal connection instructions. This terminal runs on the VM.
3. Upload the course ZIP through your approved transfer method (Bastion file transfer when available,
   or scp from your computer). Extract it and enter `ai103-hands-on-academy`.
4. Check `python3 --version` (Ubuntu 24.04 normally provides Python 3.12). On this dedicated VM install the venv/unzip packages with `sudo apt-get update` then `sudo apt-get install -y python3-venv unzip`. If your approved image differs, use its repository instructions. Create and activate a venv:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

5. Speech: follow the SDK's Linux native-dependency instructions for your OS, then
   `python -m pip install -r requirements/speech.txt`. Install OS libraries only on this dedicated VM.
   Copy `.env.example` to `.env`, populate Speech key/region privately using a terminal editor,
   `chmod 600 .env`, and run `python labs/27_speech_transcription_synthesis_translation/run.py --live`.
   Expect a WAV and recognized text under outputs. Never commit/upload your populated .env.
6. MCP: `python -m pip install -r requirements/mcp.txt`, then
   `python labs/21_mcp_server_and_client/run.py --live`. Expect public_policy discovery and result.
   No inbound network port is needed for stdio MCP.
7. Fabric: install Microsoft ODBC Driver 18 using the official instructions for your actual distro,
   then requirements/fabric.txt. Follow [Fabric connection](../fabric/README.md).
8. Copy only sanitized outputs back to your volume, delete local credentials, stop/deallocate or
   delete the learning VM and associated chargeable disks/IPs after the experiment.

If a required OS/package is unavailable, record the prerequisite as blocked. Do not mark a
fixture as a native SDK success.

References:
- https://learn.microsoft.com/en-us/azure/ai-services/speech-service/quickstarts/setup-platform?tabs=linux
- https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server
