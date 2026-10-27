# Purpose: Extract domain-specific structured facts
# Learn: Validate a domain schema and compare extracted facts with the supplied source text.
# Run: Import databricks/extensions/06_domain_extraction.py as a Databricks source notebook. Start live=false; read extensions/domain_extraction/RUNBOOK.md.

"""Domain-specific text extraction: JSON schema plus deterministic evidence checks."""
import json
from academy.common import args, save
from academy.cloud import chat
opts = args('Extract a compliance-oriented retail case summary')
text = 'Customer reports K100 unused. Receipt is missing. They request a return, not cancellation.'
schema = {'type':'object','properties':{
    'product':{'type':'string'},'topic':{'type':'string'},'summary':{'type':'string'},
    'tone':{'type':'string'},'missing_evidence':{'type':'array','items':{'type':'string'}}},
    'required':['product','topic','summary','tone','missing_evidence'],'additionalProperties':False}
if opts.live:
    response = chat([{'role':'system','content':'Extract only user-stated facts. Distinguish missing evidence from negative facts. Never decide eligibility.'},
                     {'role':'user','content':text}],
                    response_format={'type':'json_schema','json_schema':{'name':'retail_case','strict':True,'schema':schema}})
    result = json.loads(response.choices[0].message.content)
    from jsonschema import validate
    validate(result, schema)
else:
    result = {'product':'K100','topic':'return','summary':'Unused item; receipt missing; return requested.',
              'tone':'neutral','missing_evidence':['receipt']}
save('06_domain_extraction.json', {'mode':'model extraction' if opts.live else 'fixture', 'extraction':result,
    'checks':{'product_found_in_evidence':result['product'] in text,'human_review_required':True}})
