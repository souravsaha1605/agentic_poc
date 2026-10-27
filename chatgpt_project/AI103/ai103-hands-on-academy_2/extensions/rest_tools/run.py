# Purpose: Call a real local HTTP tool
# Learn: Observe request/response transport using a loopback server with a bounded client timeout and shutdown.
# Run: Import databricks/extensions/12_rest_transport.py as a Databricks source notebook. Start live=false; read extensions/rest_tools/RUNBOOK.md.

"""Start a loopback server, call its fixed endpoint, and always stop it.

This exercise demonstrates HTTP boundaries without exposing a public service.
"""
import json
import threading
import urllib.request
from http.server import HTTPServer
from pathlib import Path
import runpy
from academy.common import save
handler = runpy.run_path(str(Path(__file__).with_name('server.py')))['Handler']
server = HTTPServer(('127.0.0.1', 0), handler)  # OS selects a free port.
worker = threading.Thread(target=server.serve_forever, daemon=True)
worker.start()
try:
    url = f'http://127.0.0.1:{server.server_port}/policy'
    with urllib.request.urlopen(url, timeout=5) as response:
        value = json.load(response)
    save('12_rest.json', {'transport': 'real local HTTP', 'policies': value})
finally:
    server.shutdown()
    server.server_close()
    worker.join(timeout=5)
