# Lab 17 instructor notes

Agent-selected retrieval is a decision pattern. It is distinct from the named Azure AI Search agentic retrieval service; evaluate query planning, access scope and final groundedness.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Use variant=azure-search after lab 09 ingestion; compare with variant=default using the local policy tool. Connect a permitted Azure Search index to the managed agent in Foundry and compare traces.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

Live mode may choose search_policy or answer without a tool. variant=default uses the local corpus; variant=azure-search uses the implemented Azure Search tool.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
