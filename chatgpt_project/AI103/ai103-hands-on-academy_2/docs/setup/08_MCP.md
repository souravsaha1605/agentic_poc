# Local MCP transport

Lab 21 uses the MCP **v1** Python SDK deliberately (`mcp>=1.12,<2`) because its explicit
ClientSession/list_tools/call_tool flow makes the protocol easy to inspect. Current MCP v2
has different APIs; do not upgrade this notebook silently. The v1 documentation is linked below.

In Databricks use supported dedicated classic compute. Run the lab's package cell, restart
Python, then set live=true. This starts a local subprocess serving only public synthetic
policy search. No network port, external account or Azure service is required. The launcher
passes PYTHONPATH so the subprocess can import academy. In a terminal install the requirement
file in a separate virtual environment if necessary and run the same script with --live.

Observe tool discovery before invocation and inspect the structured result. The server's stdout
belongs to the protocol; use stderr for diagnostic logging. Add one typed read-only tool and
observe its schema. Test an invalid argument and an unknown tool name.

For remote MCP, study authenticated Streamable HTTP transport and scoped access. Allowlist
servers and tools; review tool-description changes; treat returned content as untrusted data.
Do not add a general shell/file/payment tool merely to demonstrate protocol capability.

If subprocess execution is blocked, run this one lab locally or on approved dedicated compute.
A contract preview is not a successful protocol run; record the difference in PROGRESS.csv.

Reference: https://py.sdk.modelcontextprotocol.io/v1/
