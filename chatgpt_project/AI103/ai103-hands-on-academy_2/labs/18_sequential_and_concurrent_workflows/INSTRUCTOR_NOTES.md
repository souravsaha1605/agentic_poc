# Lab 18 instructor notes

Concurrency changes latency, not total work. Limit fan-out against provider quotas and decide whether partial results are safe to use.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Make policy depend on an order ID and explain why that branch must wait. Add a timeout. Compare asyncio.gather with a loop of awaits.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

Concurrent work usually takes roughly the slower branch time. --variant failure returns one result plus one error.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
