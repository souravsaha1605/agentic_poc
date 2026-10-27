# Lab 09 instructor notes

Hybrid combines lexical and vector retrieval; semantic ranking reranks candidates. Security filtering and result quality are separate requirements.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Run --live --variant ingest once, then --live. Ask about K100 and a paraphrase. Change tenant only in trusted test code and compare permitted results.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

Ingest writes five synthetic records; query mode compares four search methods. Private partner evidence is filtered out.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
