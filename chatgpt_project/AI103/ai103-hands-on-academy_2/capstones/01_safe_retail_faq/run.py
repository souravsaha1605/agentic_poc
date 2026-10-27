# Purpose: Combine a safe retail FAQ pipeline
# Learn: Trace safety, tenant-filtered retrieval, grounded answers and citations through one application.
# Run: Import databricks/capstones/01_safe_retail_faq.py as a Databricks source notebook. Start live=false; read capstones/01_safe_retail_faq/RUNBOOK.md.

"""RAG + tenant-scoped retrieval + moderation + cache + small evidence report."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
import time
from academy.common import args,save
from academy.domain import ALICE,TTLCache
from academy.flows import rag
from academy.search import search
opts=args('Safe FAQ capstone')
cache=TTLCache()
key=cache.key(ALICE,opts.question,'policy-v1-prompt-v1')
start=time.perf_counter()
result=rag(opts.question,opts.live,retriever=search if opts.live else None)
cache.put(key,result,30)
save('capstone01.json',{'execution':'Azure' if opts.live else 'local deterministic', 'answer':result,
 'second_request_cache_hit':cache.get(key) is not None,'elapsed_ms':round((time.perf_counter()-start)*1000,2),
 'cache_scope':list(key),'quality_check':'Review each claim against the returned source IDs'})
