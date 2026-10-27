# Purpose: Generate, resume and remix video jobs
# Learn: Persist an asynchronous job ID, poll with limits and resume without submitting a duplicate paid job.
# Run: Import databricks/labs/29_video_generation_and_editing.py as a Databricks source notebook. Start live=false; read labs/29_video_generation_and_editing/RUNBOOK.md.

"""Generate, resume, or remix a short video through the current Sora 2 API."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import args, save, env
from academy.video import render
opts = args('Sora 2: submit once and retain the job ID')
if opts.live:
    prompt = 'A fictional illustrated kettle on a counter, slow camera movement, no logos.'
    if opts.variant == 'remix':
        prompt = 'Change only the background to pale blue; keep the illustrated kettle.'
    result = render(prompt, opts.file,
                    resume_id=env('VIDEO_ID') if opts.variant == 'resume' else None,
                    remix_id=env('VIDEO_ID') if opts.variant == 'remix' else None)
else:
    result = {'mode': 'lifecycle preview; no video service call',
              'states': ['queued', 'in_progress', 'completed or failed'],
              'variants': ['default', 'resume', 'remix'],
              'next': 'Follow RUNBOOK.md. The old video/generations/jobs API is not used.'}
save('29_video.json', result)
