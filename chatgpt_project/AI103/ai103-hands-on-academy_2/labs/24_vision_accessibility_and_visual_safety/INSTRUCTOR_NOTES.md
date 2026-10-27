# Lab 24 instructor notes

Use multimodal understanding for visual context, OCR for characters, and structured analyzers for downstream fields. Apply visual and text policy checks at the right stages.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Use receipt.png to compare OCR-like output with a caption. Add harmless text that asks the model to change its task and inspect behavior. Check unsupported claims about hidden damage.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

Alt text and a longer description grounded in the supplied image, plus visual moderation results.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
