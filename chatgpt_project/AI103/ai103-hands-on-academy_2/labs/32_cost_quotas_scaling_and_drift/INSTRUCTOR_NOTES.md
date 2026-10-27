# Lab 32 instructor notes

Retries do not create capacity. Use queueing, traffic shaping, quota planning and tested routing. Diagnose drift by input mix, retrieval freshness and quality separately.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Replace rates with your deployment pricing. Double context and agent turns. Compare cached vs uncached traffic. Track 429 rate, p95 latency and evaluation changes across releases.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

A transparent estimate using sample rates, not a claim of current Azure pricing.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
