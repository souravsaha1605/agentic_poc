# Purpose: Probe prompt injection defenses
# Learn: Treat retrieved text as untrusted data and distinguish a local rule from a hosted safety check.
# Run: Import databricks/labs/05_prompt_injection_and_red_teaming.py as a Databricks source notebook. Start live=false; read labs/05_prompt_injection_and_red_teaming/RUNBOOK.md.

"""Lab 05: Prompt injection and red teaming. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import args,read,save
from academy.domain import local_guard
from academy.cloud import shield
opts=args('Measure a small adversarial suite')
results=[]
for case in read('data/attacks.json'):
    if opts.live:
        r=shield(case['prompt'],case['documents'])
        blocked=r.get('userPromptAnalysis',{}).get('attackDetected',False) or any(d.get('attackDetected') for d in r.get('documentsAnalysis',[]))
    else:
        blocked=local_guard(case['prompt'])
    results.append({'id':case['id'],'expected_attack':case['attack'],'detected':blocked,'correct':blocked==case['attack']})
save('05_redteam.json',{'mode':'Prompt Shields' if opts.live else 'weak keyword baseline', 'cases':results,
 'accuracy':sum(r['correct'] for r in results)/len(results),'note':'Tiny diagnostic set, not a safety certification'})
