# Lab 29 instructor notes

A client timeout is not a server cancellation. Record job state and inspect before creating another paid job. Track reference rights, visual policy and human review.

## Read the implementation

Start at run.py. Identify which work happens locally and which function crosses an Azure boundary.
Follow the import to src/academy only when needed; do not try to learn the entire package at once.
Look for argument validation before a tool/service call and for explicit error handling after it.

## Exercise debrief

Pass --file data/media/video_reference.png, then remix a completed video ID. Compare reference changes, supported resolution and duration. Edit with a new prompt and inspect temporal consistency.

For each experiment record **prediction → observation → explanation → production implication**.
A successful happy-path output is insufficient: demonstrate the failure case and explain whether
it is a code, permission, network, quota, data or model-behavior problem. Inspect returned metadata
and source support rather than assuming a fluent answer is correct.

## Evidence standard

A printed job ID and outputs/generated.mp4 when the supported service finishes. Preview/access availability can block this lab.

Mark local and Azure verification separately. The answer above is a design guide, not a claim
that your subscription has all required capabilities or that the small dataset measures production quality.

Reference-image experiment: use the included `data/media/video_reference.png` (1280x720). Upload it to your volume and set input_file to that path. It matches the default VIDEO_SIZE.
