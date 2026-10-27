# Purpose: Evaluate a dataset and enforce a quality gate
# Learn: Distinguish deterministic checks from model judges and inspect examples behind aggregate scores.
# Run: Import databricks/labs/23_evaluation_datasets_and_regression_gates.py as a Databricks source notebook. Start live=false; read labs/23_evaluation_datasets_and_regression_gates/RUNBOOK.md.

"""Lab 23: Evaluation datasets and regression gates. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import args,save,read,env
from academy.flows import agent,rag
opts=args('Evaluate retrieval/tool behavior or use an Azure model judge')
if opts.live:
    from azure.ai.evaluation import GroundednessEvaluator,RelevanceEvaluator
    config={'azure_endpoint':env('AZURE_OPENAI_ENDPOINT'),'azure_deployment':env('MODEL_REASONING'),
            'api_key':env('AZURE_OPENAI_API_KEY'),'api_version':'2024-10-21'}
    response='Unused items can be returned within 30 days with a receipt.'
    context='Return policy: unused items, 30 days, receipt required.'
    result={'groundedness':GroundednessEvaluator(model_config=config)(query='Can I return an unused item?',response=response,context=context),
            'relevance':RelevanceEvaluator(model_config=config)(query='Can I return an unused item?',response=response)}
else:
    results=[]
    for c in read('evals/cases.json'):
        try:
            r=agent(c['query'])
            intent='order' if r['tool']=='order_status' else 'policy'
            correct=r['tool']==c['tool'] and r['arguments']==c['arguments']
            allowed=True
        except PermissionError:
            intent='order'
            correct=c['tool']=='order_status'
            allowed=False
        results.append({'id':c['id'],'intent_ok':intent==c['intent'],'tool_ok':correct,'adherence_ok':allowed==c['allowed']})
    result={'mode':'deterministic local dispatcher evaluation, NOT model quality', 'cases':results,
      'metrics':{k:sum(r[k] for r in results)/len(results) for k in ('intent_ok','tool_ok','adherence_ok')}}
    if result['metrics']['adherence_ok']<1:
        raise RuntimeError('Security regression gate failed')
save('23_evaluation.json',result)
