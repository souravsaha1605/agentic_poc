# Lab 11 instructor notes

A correct retrieved passage does not guarantee a faithful answer. Evaluate retrieval and generation separately and retain provenance.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Ask an unsupported question. Add malicious text to a document in a disposable index. Compare retrieval hit rate with answer groundedness; inspect the first failing stage.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

An answer and source IDs, or explicit insufficient evidence. Live mode uses Azure Search, model, moderation and Prompt Shields.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
