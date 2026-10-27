# Lab 19 instructor notes

More agents are not automatically better. Measure quality gains, coordination overhead and privilege boundaries. Evaluate observable decisions and concise rationales rather than hidden chain of thought.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Compare final quality and latency with one model call. Implement a two-round group discussion with a fixed speaker order and stop condition. Give specialists disjoint tool lists.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

Three bounded stages: draft, review, revision. --variant handoff passes an explicit state object to a specialist.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
