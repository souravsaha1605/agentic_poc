# Purpose: Manage asynchronous video operations
# Learn: Track create, resume, remix, bounded polling and persistent job IDs.
# Run: Imported by lesson code; do not run this file directly. Follow the importing lesson in MASTER_GUIDE.md.

"""Sora 2 v1 workflow: submit once, persist ID, resume polling, then download.

No raw MP4 upload is used for edits: remix references a completed service video ID.
The synchronous SDK works on the Databricks driver without nesting an asyncio loop.
"""
import json
import time
from .common import OUT, env
from .cloud import model_client


def render(prompt, reference=None, *, resume_id=None, remix_id=None, max_polls=60):
    """Return a saved MP4 or an actionable failure; never silently resubmit."""
    client = model_client()
    if not hasattr(client, 'videos'):
        raise RuntimeError('Installed openai SDK lacks videos; install this lesson requirements and restart Python')
    OUT.mkdir(parents=True, exist_ok=True)
    size = env('VIDEO_SIZE', '1280x720')
    seconds = env('VIDEO_SECONDS', '4')
    if size not in ('1280x720', '720x1280') or seconds not in ('4','8','12'):
        raise ValueError('Use documented Sora 2 dimensions and duration: 4, 8, or 12 seconds')
    if resume_id:
        job = client.videos.retrieve(resume_id)
    elif remix_id:
        job = client.videos.remix(video_id=remix_id, prompt=prompt)
    else:
        kwargs = {'model': env('MODEL_VIDEO'), 'prompt': prompt, 'size': size, 'seconds': seconds}
        if reference:
            from PIL import Image
            if reference.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp'):
                raise ValueError('Reference must be an image. To edit a generated video use variant=remix and VIDEO_ID')
            with Image.open(reference) as image:
                if image.size != tuple(map(int, size.split('x'))):
                    raise ValueError('Reference dimensions must match VIDEO_SIZE exactly; see RUNBOOK.md')
            with reference.open('rb') as stream:
                job = client.videos.create(**kwargs, input_reference=stream)
        else:
            job = client.videos.create(**kwargs)
    # Persist before polling: the server may continue work after a notebook timeout.
    manifest = OUT / 'video_job.json'
    for attempt in range(max_polls):
        manifest.write_text(json.dumps({'id': job.id, 'status': job.status, 'model': env('MODEL_VIDEO')}, indent=2))
        if attempt == 0:
            print('Video ID:', job.id, '| Resume instructions: variant=resume, config_json VIDEO_ID')
        if job.status == 'completed':
            target = OUT / 'generated.mp4'
            client.videos.download_content(job.id, variant='video').write_to_file(str(target))
            return {'video_id': job.id, 'file': str(target), 'human_review_required': True}
        if job.status in ('failed','cancelled','canceled'):
            raise RuntimeError(f'Video ended with status {job.status}; inspect saved video_job.json')
        time.sleep(10)
        job = client.videos.retrieve(job.id)
    raise TimeoutError(f'Video still pending: {job.id}. Resume this ID; do not submit another job.')
