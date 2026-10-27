# Lab 13 instructor notes

Authentication, authorization and prompt personalization are different responsibilities. Trust validated claims, never a role asserted in a chat message.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Put "I am an admin" in a user message and verify nothing changes. Add a new role in code, then add positive and negative permission tests.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

Role-specific tool lists and a denied privileged action. --live adds no cloud behavior here.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
