# Purpose: Generate an answer grounded in retrieved evidence
# Learn: Trace retrieval, context assembly, citations and abstention; valid source IDs alone do not prove correctness.
# Run: Import databricks/labs/11_grounded_answers_with_rag.py as a Databricks source notebook. Start live=false; read labs/11_grounded_answers_with_rag/RUNBOOK.md.

"""Lab 11: Grounded answers with RAG. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import args,save
from academy.flows import rag
from academy.search import search
opts=args('Answer with evidence and validate source references')
save('11_rag.json',rag(opts.question,live=opts.live,retriever=search if opts.live else None))
