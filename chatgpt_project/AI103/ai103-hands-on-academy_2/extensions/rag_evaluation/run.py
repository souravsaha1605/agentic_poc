# Purpose: Evaluate the complete RAG application
# Learn: Check retrieved citations, safety and expected responses across a small regression dataset.
# Run: Import databricks/extensions/23_rag_regression.py as a Databricks source notebook. Start live=false; read extensions/rag_evaluation/RUNBOOK.md.

"""Evaluate actual RAG outputs, separating deterministic checks from human quality review."""
import json
from pathlib import Path
from academy.common import args, save
from academy.flows import rag
from academy.search import search
opts = args('Run a small held-out-style RAG regression set')
rows = []
for case in json.loads(Path(__file__).with_name('cases.json').read_text()):
    answer = rag(case['question'], live=opts.live, retriever=search if opts.live else None)
    checks = {'abstention':answer['uncertain']==case['abstain'],
              'source':case['expected_source'] is None or case['expected_source'] in answer['sources'],
              'required_fact':case['must_include'] is None or case['must_include'] in answer['answer']}
    rows.append({'id':case['id'],'answer':answer,'checks':checks,'passed':all(checks.values())})
save('23_rag_regression.json',{'mode':'live RAG outputs' if opts.live else 'local deterministic RAG',
                              'passed':sum(x['passed'] for x in rows),'total':len(rows),'cases':rows,
                              'limitation':'Substring/source checks do not establish claim-level groundedness. Review answers manually.'})
if not all(x['passed'] for x in rows):
    raise RuntimeError('RAG regression failed; inspect saved cases before changing a threshold')
