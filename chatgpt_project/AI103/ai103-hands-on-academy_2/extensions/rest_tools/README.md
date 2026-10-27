# rest tools

Start with [RUNBOOK.md](RUNBOOK.md).

This notebook uses a real loopback HTTP server, client timeout and finally cleanup. No Azure key
is needed. If loopback/threading is blocked by workspace policy, run `python extensions/rest_tools/run.py`
on the Azure VM fallback. Expect permitted policy JSON. The standalone server.py blocks intentionally;
use run.py for a complete start/call/stop lifecycle.
