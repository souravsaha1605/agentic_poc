# Lab 26 instructor notes

Preserve page/time/region evidence when generating downstream chunks. Capability names and preview options vary; record the API and analyzer version used.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Create the custom receipt analyzer in PORTAL.md. Change CU_ANALYZER to its ID. Try imageSearch and videoSearch with appropriate media. Historical pro mode is retired; compare GA analysis with the current agentic document extension and read azure_execution/content_understanding.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

A completed analysis with fields/markdown/provenance according to the chosen analyzer; live polling has a deadline.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
