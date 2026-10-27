# Lab 22 instructor notes

Find the first abnormal operation. Head sampling is decided early; tail sampling needs a collector/backend that can evaluate completed traces. Sampling is not a substitute for redaction.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Run a repeated tool call and inspect the loop stop in flows.agent. Compare serial and parallel spans. Add memory.read and approval.request spans using IDs, not raw payloads.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

A parent and child span appear in Application Insights in live mode; no prompt content is attached.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
