# Lab 06 instructor notes

The language → PII → entities → key phrases order is a useful course pattern, not a universal mandated order. Sentiment can prioritize a case but cannot authorize a refund.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Try Hindi and mixed-language input. Check supported languages per operation. Inspect whether the redaction misses an order ID; add a domain-specific rule if needed.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

Live service output contains redacted text and categories. Offline mode is a labeled saved example.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
