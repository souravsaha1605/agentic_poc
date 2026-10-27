# Purpose: Submit a request to a Logic App
# Learn: Treat the signed trigger URL as a secret and distinguish submission from completed human approval.
# Run: Import databricks/extensions/20_logic_app_submit.py as a Databricks source notebook. Start live=false; read extensions/logic_app_submit/RUNBOOK.md.

"""Submit a synthetic approval once. The workflow executes in Azure, not Databricks."""
from academy.common import args, env, save
from academy.cloud import request
opts = args('Submit the dedicated learning Logic App request')
if opts.live:
    import uuid
    # The callback URL is a secret; do not print it or include it in saved results.
    payload = {'request_id':str(uuid.uuid4()),'order_id':'ORD-1001',
               'amount_paise':150000,'currency':'INR','evidence_ids':['returns-v1','refunds-v1']}
    response = request('POST', env('LOGIC_APP_TRIGGER_URL'), body=payload, timeout=30)
    if response.status_code != 202:
        raise RuntimeError('Expected 202: place Response before approval in the Logic App designer')
    result = {'submitted':True, 'response':response.json(), 'money_moved':False}
else:
    result = {'mode':'request preview','next':'Configure azure_execution/logic_apps before live=true'}
save('20_logic_app.json',result)
