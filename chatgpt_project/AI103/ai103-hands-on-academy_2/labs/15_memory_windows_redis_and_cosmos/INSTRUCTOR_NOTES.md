# Lab 15 instructor notes

Partitioning helps organization/performance; it is not authorization by itself. Enforce user access in the service and scope credentials. Summaries are lossy and can carry injected content.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Expire a session. Compare last-N messages, a token budget and a summary. Ask what a summary might lose. Add a delete-memory operation and test it.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

Alice sees her session; Bob sees an empty list. Live examples create and remove synthetic records.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
