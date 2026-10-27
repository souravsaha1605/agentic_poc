# Lab 21 instructor notes

MCP does not automatically grant permission or make tool output trustworthy. Pin a protocol SDK generation and keep tool permissions narrow.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Add one read-only tool with a typed argument. Send an invalid type. Explain how authentication changes if this server is exposed over HTTP. Review v1 versus v2 migration notes before upgrading.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

Protocol discovery exposes public_policy and invocation returns policy evidence. --live here means real local MCP transport, not Azure.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
