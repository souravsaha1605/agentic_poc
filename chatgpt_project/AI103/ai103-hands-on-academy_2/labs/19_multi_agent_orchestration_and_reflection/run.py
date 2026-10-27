# Purpose: Coordinate agents and bounded reflection
# Learn: Separate writer/reviewer responsibilities, handoff and stop conditions; critiques can still be wrong.
# Run: Import databricks/labs/19_multi_agent_orchestration_and_reflection.py as a Databricks source notebook. Start live=false; read labs/19_multi_agent_orchestration_and_reflection/RUNBOOK.md.

"""Lab 19: Multi agent orchestration and reflection. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import args,save
from academy.cloud import chat
opts=args('Compare orchestrated roles and one bounded critique')
policy='Unused items may be returned within 30 days with a receipt. Never claim a payment was made.'
def role(name,instruction,text):
    if opts.live:
        return chat([{'role':'system','content':instruction},{'role':'user','content':text}]).choices[0].message.content
    return {'specialist':'Policy supports a 30-day return with receipt.','reviewer':'Check receipt and unused condition; no transaction authorized.',
            'writer':'Unused products can be returned within 30 days with a receipt.'}[name]
events=[]
if opts.variant=='handoff':
    state={'question':opts.question,'evidence':policy,'owner':'returns_specialist'}
    draft=role('specialist','Handle returns only. Use the supplied evidence.',str(state))
    events.append('support -> returns specialist')
else:
    draft=role('specialist','Find the relevant rule in the evidence. Do not invent a rule.',policy+' Question: '+opts.question)
    events.append('manager -> specialist')
review=role('reviewer','Check the draft against evidence. Give brief issues only, no hidden reasoning.',policy+' Draft: '+str(draft))
final=role('writer','Revise once using evidence and review. Do not claim actions occurred.',policy+' Draft: '+str(draft)+' Review: '+str(review))
events+=['reviewer','one revision','stop']
save('19_orchestration.json',{'mode':'real role-specific model calls' if opts.live else 'scripted local outputs',
 'events':events,'draft':draft,'review':review,'final':final,'model_call_limit':3})
