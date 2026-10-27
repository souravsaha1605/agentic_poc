# Purpose: Read the local policy HTTP endpoint
# Learn: Observe a fixed allowlisted URL and client timeout.
# Run: Optional terminal demonstration after starting server.py: python extensions/rest_tools/client.py. Prefer the managed notebook for Databricks.

import json,urllib.request
# Fixed allowlisted destination, never a URL proposed by the model.
with urllib.request.urlopen('http://127.0.0.1:8765/policy',timeout=5) as response:
    print(json.dumps(json.load(response),indent=2))
