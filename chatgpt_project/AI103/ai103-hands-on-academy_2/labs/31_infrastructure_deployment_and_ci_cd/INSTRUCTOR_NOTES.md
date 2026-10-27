# Lab 31 instructor notes

Use workload federation for CI instead of stored client secrets. Scope roles to the workload. Private networking needs DNS and a client path; a private endpoint alone is incomplete.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Run the evaluation gate before changing prompts. Inspect a Bicep what-if result. Revoke an identity permission and test the deployed failure. Record a rollback procedure.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

All infrastructure and deployment files exist. Cloud deployment is an explicit guided workflow.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
