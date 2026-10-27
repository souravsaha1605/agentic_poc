# Purpose: Generate and edit images
# Learn: Distinguish text generation from mask-based edits and check model-specific media requirements.
# Run: Import databricks/labs/28_image_generation_and_mask_editing.py as a Databricks source notebook. Start live=false; read labs/28_image_generation_and_mask_editing/RUNBOOK.md.

"""Lab 28: Image generation and mask editing. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import args,save,ROOT
from academy.media import image_job
opts=args('Generate or edit one image')
if opts.live:
    edit=opts.variant=='edit'
    result=image_job('A simple fictional kettle product illustration on a pale blue background, no logo.',
       (opts.file or ROOT/'data/media/product.png') if edit else None,
       ROOT/'data/media/mask.png' if edit else None)
else:result={'mode':'request design only','generation':'text -> image','edit':'image + matching PNG mask + instruction -> image',
             'fixture_mask':'transparent background regions are editable; opaque product region is protected'}
save('28_images.json',result)
