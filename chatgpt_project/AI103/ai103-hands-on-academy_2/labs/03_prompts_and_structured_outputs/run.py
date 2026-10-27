# Purpose: Request structured model output
# Learn: Separate prompt instructions from strict output shape and validate returned JSON.
# Run: Import databricks/labs/03_prompts_and_structured_outputs.py as a Databricks source notebook. Start live=false; read labs/03_prompts_and_structured_outputs/RUNBOOK.md.

"""Lab 03: Prompts and structured outputs. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
import json
from academy.common import args,save
from academy.flows import SCHEMA
from academy.domain import validate_answer
from academy.cloud import chat
opts=args('Validate answer structure and source references')
if opts.live:
    r=chat([{'role':'system','content':'Answer concisely from the supplied evidence only. Return the required schema.'},
      {'role':'user','content':'Question: '+opts.question+' Evidence [returns-v1]: unused items can be returned within 30 days.'}],
      response_format={'type':'json_schema','json_schema':{'name':'policy_answer','strict':True,'schema':SCHEMA}})
    obj=json.loads(r.choices[0].message.content)
else:
    obj={'answer':'Unused items: 30 days.','sources':['returns-v1'],'uncertain':False}
save('03_structured.json',validate_answer(obj,{'returns-v1'}))
