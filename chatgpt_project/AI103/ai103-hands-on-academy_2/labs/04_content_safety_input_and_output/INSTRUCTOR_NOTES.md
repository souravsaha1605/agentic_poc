# Lab 04 instructor notes

Content moderation does not authorize tools or reliably stop every injection. Defense includes filters, validation, access control and review.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Change the threshold and discuss false positives. Use the portal test samples. Disconnect the service and observe that a live call fails rather than claiming the content is safe.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

Local scores 4 and 6 are blocked. Live output includes the actual service categories.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
