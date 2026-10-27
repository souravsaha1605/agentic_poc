# Purpose: Analyze content with Content Understanding
# Learn: Read structured analyzer output and understand endpoint, API version and analyzer selection.
# Run: Import databricks/labs/26_content_understanding_analyzers.py as a Databricks source notebook. Start live=false; read labs/26_content_understanding_analyzers/RUNBOOK.md.

"""Lab 26: Content Understanding analyzers. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import args,save,ROOT,fixture
from academy.media import understand
opts=args('Run a Content Understanding analyzer')
path=opts.file or ROOT/'data/media/receipt.png'
save('26_content_understanding.json',understand(path) if opts.live else fixture('content_understanding'))
