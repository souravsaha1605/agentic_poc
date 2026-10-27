# Lab 05 instructor notes

Red teaming is a repeatable measurement process. Use a scoped attack dataset, observable outcomes, fixes and regression gates. PyRIT/Foundry automated red teaming expands this beyond the small custom harness.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Add an attack inside a receipt or search result. Add a benign prompt mentioning system design. Record false positives and negatives separately. Run after changing a tool or prompt.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

The weak local baseline misses indirect and paraphrased attacks. Live mode uses Prompt Shields.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
