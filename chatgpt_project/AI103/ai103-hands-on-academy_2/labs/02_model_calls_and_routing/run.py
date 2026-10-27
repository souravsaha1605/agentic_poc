# Purpose: Compare and route model calls
# Learn: Choose deployments by task needs and explain the latency, cost and capability tradeoff.
# Run: Import databricks/labs/02_model_calls_and_routing.py as a Databricks source notebook. Start live=false; read labs/02_model_calls_and_routing/RUNBOOK.md.

"""Lab 02: Model calls and routing. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
import time
from academy.common import args,save,env
from academy.cloud import chat
opts=args('Compare two model deployments on the same question')
if opts.live:
    results=[]
    route='MODEL_REASONING' if any(term in opts.question.lower() for term in ('explain','compare','exception')) else 'MODEL_SMALL'
    selected=[route] if opts.variant=='route' else ['MODEL_SMALL','MODEL_REASONING']
    for deployment in selected:
        start=time.perf_counter()
        response=chat([{'role':'user','content':opts.question}],deployment=deployment)
        results.append({'deployment':env(deployment),'answer':response.choices[0].message.content,
          'latency_ms':round((time.perf_counter()-start)*1000),'usage':response.usage.model_dump() if response.usage else None})
else:
    results={'mode':'local routing rule only','route':'MODEL_REASONING' if any(term in opts.question.lower() for term in ('explain','compare','exception')) else 'MODEL_SMALL'}
save('02_models.json',results)
