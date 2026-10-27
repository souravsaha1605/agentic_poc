# Lab 20 instructor notes

Use an authenticated decision endpoint and immutable payload. Never accept an approver name supplied by the model as proof of authority.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Run --variant reject. Expire a request. Attempt self-approval and non-supervisor approval. Follow the portal guide to persist requests and decisions asynchronously.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

Pending → approved → executed, or pending → rejected. No external transaction occurs.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
