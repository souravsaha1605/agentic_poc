# Lab 25 instructor notes

OCR text is insufficient for reliable totals. Validate currency, line-item arithmetic and provenance; route uncertainty to review.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Run --variant layout and compare fields with receipt mode. Blur a copy locally with an image editor and compare confidence. In Document Intelligence Studio, label a small custom model dataset and inspect train/test separation.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

Extracted receipt fields or page/table structure. Offline fields are explicitly synthetic fixtures.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
