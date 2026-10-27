# Lab 27 instructor notes

A synthetic TTS round trip is a wiring test, not real recognition accuracy. Measure word error rate on representative held-out audio. Do not assume every API returns a confidence score.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Record your own short WAV; use --file. Compare accents/noise and inspect detailed results. In Speech Studio create a custom project, upload labeled audio, evaluate before training, then deploy if justified.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

A WAV file and recognized transcript. --variant translate produces a Hindi translation; --variant custom uses your deployed custom endpoint.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.
