# Purpose: Build an enterprise research assistant
# Learn: Combine authorized evidence, parallel retrieval and bounded review; compare synthetic analytics with Fabric.
# Run: Import databricks/capstones/04_enterprise_research_assistant.py as a Databricks source notebook. Start live=false; read capstones/04_enterprise_research_assistant/RUNBOOK.md.

"""Independent source reads + role separation + bounded review of a grounded draft."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
import asyncio,json
from academy.common import args,save,run_async
from academy.cloud import chat
from academy.domain import retrieve
from academy.search import search
opts=args('Combine analytical and policy evidence with a bounded review')
async def analytical():
    if opts.live and opts.variant == 'fabric':
        from academy.enterprise import sales
        return await asyncio.to_thread(sales)
    # Default remains an explicitly labeled snapshot fixture.
    return {'source':'synthetic-monthly-sales','product':'K100','units':120,'period':'2026-09'}
async def policies():
    return await asyncio.to_thread(search,opts.question) if opts.live else retrieve('warranty K100')
async def main():
    sales,policy=await asyncio.gather(analytical(),policies())
    evidence={'sales':sales,'policies':policy}
    if opts.live:
        draft=chat([{'role':'system','content':'Summarize the supplied evidence only. State source freshness and uncertainty.'},
                    {'role':'user','content':json.dumps(evidence)}]).choices[0].message.content
        review=chat([{'role':'system','content':'Identify unsupported claims in this draft against evidence. Return a brief checklist, not internal reasoning.'},
                     {'role':'user','content':json.dumps({'draft':draft,'evidence':evidence})}]).choices[0].message.content
    else:
        draft='K100 sold 120 units in the synthetic September snapshot. Its policy states a 12-month manufacturing warranty.'
        review='Snapshot is historical; current inventory requires an operational source.'
    return {'evidence':evidence,'draft':draft,'review':review,'max_model_calls':2,
            'limitations':'Default analytics is synthetic; variant=fabric reads the configured endpoint. No live inventory or write permission is granted.'}
save('capstone04.json',run_async(main()))
