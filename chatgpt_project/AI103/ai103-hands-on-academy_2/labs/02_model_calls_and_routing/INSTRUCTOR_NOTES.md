# Lab 02 instructor notes

Choose by task performance, context length, modality, latency and price. A small model can outperform a larger one on a specialized task; routing needs evaluation.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Ask a short classification question and a policy comparison. Record quality before picking a cheaper model. Try a supported code task. Change generation settings only after checking model support.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

Live mode returns two answers, actual token usage when provided, and timings; no invented cost figures.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
