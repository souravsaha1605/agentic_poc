# Lab 28 instructor notes

Generation is not image analysis. Edit controls and model support differ. Never claim a mask guarantees exact pixel preservation; visually inspect and evaluate.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Compare --live and --live --variant edit. Change prompt, supported quality and aspect ratio one at a time. Review visual moderation, brand rules and provenance before publication.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

outputs/generated.png or edited.png in live mode; requests use a configured deployment and preview API version.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
