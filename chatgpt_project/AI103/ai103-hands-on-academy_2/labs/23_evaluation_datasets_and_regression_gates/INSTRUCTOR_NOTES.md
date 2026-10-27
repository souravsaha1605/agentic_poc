# Lab 23 instructor notes

The handbook example thresholds are project targets, not Microsoft passing criteria. A judge model can be wrong; inspect disagreements with human reviewers.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Add 20–30 labeled cases including ambiguous intent and forbidden orders. Capture actual live tool traces for tool-call accuracy. Compare prompts on a held-out set; do not tune on every evaluation case.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

Separate metrics for the local dispatcher. Live mode calls model-assisted groundedness and relevance evaluators.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
