# Lab 16 instructor notes

Do not mix classic projects 1.x samples with new projects 2.x. Resource inference endpoints and project endpoints are different.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Start a new conversation and repeat the recall question. Inspect the version in Foundry. Change instructions, create another version and compare behavior.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

The second response recalls K100. The agent version remains for portal inspection; the sample conversation is deleted.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
