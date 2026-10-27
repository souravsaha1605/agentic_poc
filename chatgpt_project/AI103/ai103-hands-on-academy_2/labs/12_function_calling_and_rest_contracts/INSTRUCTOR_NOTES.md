# Lab 12 instructor notes

Never let a model choose arbitrary URLs or SQL. Validate tool schemas and enforce ownership in the backend even if the prompt says access is restricted.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Ask for ORD-1002 while signed in as Alice. Try an unknown tool name in execute_tool. Inspect tool schemas and compare auto, none and forced tool choice in a separate read-only request.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

Use --question "Check ORD-1001". Local mode identifies the order deterministically; live mode shows actual model-selected tools and call IDs.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
