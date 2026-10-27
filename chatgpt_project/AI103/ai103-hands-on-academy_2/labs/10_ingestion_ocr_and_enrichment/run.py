# Purpose: Plan OCR and enrichment ingestion
# Learn: Follow the portal indexer exercise and inspect ingestion errors; the notebook is a local planning exercise.
# Run: Import databricks/labs/10_ingestion_ocr_and_enrichment.py as a Databricks source notebook. Start live=false; read labs/10_ingestion_ocr_and_enrichment/RUNBOOK.md.

"""Lab 10: Ingestion OCR and enrichment. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
import hashlib
from academy.common import args,ROOT,save
from academy.domain import chunk
opts=args('Build a local ingestion manifest; use PORTAL.md for cloud enrichment')
if opts.live:
    raise SystemExit('This lab is portal-led. Follow PORTAL.md to create and inspect an Azure indexer/skillset.')
records=[]
for p in sorted((ROOT/'data/documents').glob('*.txt')):
    text=p.read_text()
    records.append({'source':p.name,'sha256':hashlib.sha256(text.encode()).hexdigest(),
       'chunks':[{'id':p.stem+'-'+str(i),'text':c} for i,c in enumerate(chunk(text,size=20,overlap=4))]})
save('10_ingestion_manifest.json',records)
