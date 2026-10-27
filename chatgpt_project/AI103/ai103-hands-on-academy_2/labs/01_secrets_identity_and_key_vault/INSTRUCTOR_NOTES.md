# Lab 01 instructor notes

Prefer managed identity on Azure. A valid token does not grant data access. Secrets Officer can manage secrets; Secrets User reads values. Neither is automatically granted by owning application code.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Remove the read role and rerun. Compare a 403 with an unauthenticated request. Rotate the dummy secret and observe a new version. Identify the principal used locally versus on Azure.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

A secret name/version and found=true; the secret value is never printed.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
