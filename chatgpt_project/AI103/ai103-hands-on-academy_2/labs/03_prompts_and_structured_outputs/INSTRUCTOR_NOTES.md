# Lab 03 instructor notes

Prompts guide behavior; schemas enforce shape; authorization and business rules remain code. Citation existence is weaker than claim-level evidence support.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Change the offline source ID to invented-v1. Add an unexpected field. Compare concise versus detailed prompt versions, and record the prompt version with results.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

Exactly answer, sources, uncertain; an unknown source ID raises ValueError.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
