# Purpose: Build and query a search index
# Learn: Compare keyword, vector, hybrid and semantic retrieval while retaining trusted tenant filters.
# Run: Import databricks/labs/09_azure_search_vector_hybrid_semantic.py as a Databricks source notebook. Start live=false; read labs/09_azure_search_vector_hybrid_semantic/RUNBOOK.md.

"""Lab 09: Azure Search vector hybrid semantic. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import args,save
from academy.domain import retrieve
from academy.search import ingest,search
opts=args('Build a small Azure Search index or query it')
if opts.live:
    if opts.variant == 'ingest':
        result = ingest()
    else:
        modes = [opts.variant] if opts.variant in ('keyword','vector','hybrid','semantic') else ['keyword','vector','hybrid','semantic']
        result = {mode: search(opts.question, mode=mode) for mode in modes}
else:
    result={'mode':'local lexical retrieval only','results':retrieve(opts.question)}
save('09_search.json',result)
