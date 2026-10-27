# Lab 14 instructor notes

A transport timeout does not prove a write failed. Query request state before retrying. Distributed payments need durable idempotency at the actual payment boundary.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Reuse a key with a different order/user and expect rejection. Set cache TTL=0 and verify a miss. Inspect cloud.request for bounded read retries and Retry-After behavior.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

Both calls report executed, but the effect count stays 1; no payment is made.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
