# Lab 10 instructor notes

An indexer schedule alone does not guarantee freshness. Track failed documents, deleted data, enrichment errors and search relevance.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Edit a source and compare its hash. Delete it and plan removal of stale index documents. Upload the synthetic receipt image to Blob Storage and inspect OCR enrichment in the portal.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

Stable source names, content hashes and chunk IDs. Cloud success is an indexer run with visible enriched fields.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
