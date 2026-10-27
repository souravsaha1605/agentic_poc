# Purpose: Index normalized multimodal evidence
# Learn: Turn extracted document/audio/video evidence into searchable records with provenance and tenant fields.
# Run: Import databricks/extensions/26_multimodal_ingestion.py as a Databricks source notebook. Start live=false; read extensions/multimodal_ingestion/RUNBOOK.md.

"""Convert Content Understanding output into provenance-bearing retrieval chunks.

Use a lab 26 JSON output as input_file. Live mode embeds and indexes those chunks.
"""
import hashlib
import json
from academy.common import args, save, read
from academy.domain import chunk
from academy.search import ingest_rows
opts = args('Convert analysis output into grounded retrieval records')
if opts.file:
    payload = json.loads(opts.file.read_text())
    analysis = payload.get('result', payload)
    source = opts.file.name
else:
    if opts.live:
        raise ValueError('Supply lab 26 output as input_file before live indexing')
    analysis = {'contents':[{'markdown':'K100 has a 12 month warranty.','startTimeMs':0,'endTimeMs':1000}]}
    source = 'explicit-offline-fixture'
contents = analysis.get('result', analysis).get('contents', [])
rows = []
for position, content in enumerate(contents):
    text = content.get('markdown') or content.get('text')
    if not text:
        continue
    provenance = {key:content[key] for key in ('startTimeMs','endTimeMs','startPageNumber','endPageNumber') if key in content}
    for index, passage in enumerate(chunk(text, 100, 20)):
        ident = hashlib.sha256(f'{source}:{position}:{index}:{passage}'.encode()).hexdigest()[:24]
        rows.append({'id':ident,'text':passage,'tenant':'retail','kind':'analysis',
                     'provenance':{'source':source,'segment':position,**provenance}})
if not rows:
    raise ValueError('No markdown/text content found. Inspect lab 26 output and analyzer selection.')
# The small Search schema has no provenance field: embed provenance in the text to retain it.
index_rows = [{**{k:r[k] for k in ('id','tenant','kind')},
               'text':r['text']+' Source: '+json.dumps(r['provenance'])} for r in rows]
result = {'chunks':rows, 'mode':'local transformation'}
if opts.live:
    result['indexing'] = ingest_rows(index_rows)
    result['mode'] = 'Azure embeddings and Search upload'
save('26_ingestion.json',result)
