# Lab 30 instructor notes

The same question can require analytical and operational sources. A search index of yesterday’s order state should not authorize today’s transaction.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Run the Fabric/OneLake setup and SQL seed. Change inventory without changing monthly sales. Try a restricted user. Run the Cosmos vector extension after enabling vector search.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

Local two-source join or a parameterized read from your Fabric SQL analytics endpoint.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
