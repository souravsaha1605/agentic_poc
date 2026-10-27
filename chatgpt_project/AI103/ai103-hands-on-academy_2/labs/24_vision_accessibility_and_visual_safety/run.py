# Purpose: Describe images and screen visual content
# Learn: Generate accessible descriptions and inspect safety results without assuming every visual policy is detected.
# Run: Import databricks/labs/24_vision_accessibility_and_visual_safety.py as a Databricks source notebook. Start live=false; read labs/24_vision_accessibility_and_visual_safety/RUNBOOK.md.

"""Lab 24: Vision accessibility and visual safety. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
import base64
from academy.common import args,save,ROOT,fixture,env
from academy.media import vision
from academy.cloud import request,cognitive_headers
opts=args('Caption an image and optionally moderate it')
path=opts.file or ROOT/'data/media/product.png'
if opts.live:
    moderation=request('POST',env('SAFETY_ENDPOINT').rstrip('/')+'/contentsafety/image:analyze?api-version=2024-09-01',
      headers=cognitive_headers('SAFETY'),body={'image':{'content':base64.b64encode(path.read_bytes()).decode()}}).json()
    blocked=any(c['severity']>=4 for c in moderation['categoriesAnalysis'])
    result={'moderation':moderation,'description':None if blocked else vision(path)}
else:
    result=fixture('vision')
save('24_vision.json',result)
