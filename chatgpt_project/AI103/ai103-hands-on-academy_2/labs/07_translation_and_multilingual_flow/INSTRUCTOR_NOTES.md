# Lab 07 instructor notes

Back-translation is a diagnostic, not proof of equivalence. Locales, proper nouns, units and policy conditions need targeted tests.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Try Bengali using target bn. Check that 30 days and receipt requirements survive. Translate a query before retrieval and compare with multilingual embedding retrieval.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

English → Hindi → English output; compare the numbers and conditions manually.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
