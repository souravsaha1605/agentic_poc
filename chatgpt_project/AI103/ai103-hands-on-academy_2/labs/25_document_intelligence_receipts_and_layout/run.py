# Purpose: Extract document fields and layout
# Learn: Compare receipt, layout, read and custom models and inspect confidence and source layout.
# Run: Import databricks/labs/25_document_intelligence_receipts_and_layout.py as a Databricks source notebook. Start live=false; read labs/25_document_intelligence_receipts_and_layout/RUNBOOK.md.

"""Lab 25: Document Intelligence receipts and layout. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import args,save,ROOT,fixture,env
from academy.media import document
opts=args('Extract fields or layout from a synthetic receipt')
path=opts.file or ROOT/'data/media/receipt.png'
model={'layout':'prebuilt-layout','read':'prebuilt-read'}.get(opts.variant,'prebuilt-receipt')
# Offline custom mode stays a fixture and must not require cloud configuration.
if opts.live and opts.variant == 'custom':
    model = env('DOCUMENT_MODEL_ID')
save('25_document.json',document(path,model) if opts.live else fixture('receipt'))
