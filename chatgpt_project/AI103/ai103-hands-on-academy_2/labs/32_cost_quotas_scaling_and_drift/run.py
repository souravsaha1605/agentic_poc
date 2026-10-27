# Purpose: Budget cost, quotas and drift checks
# Learn: Interpret capacity and regression signals; local estimates are not subscription billing measurements.
# Run: Import databricks/labs/32_cost_quotas_scaling_and_drift.py as a Databricks source notebook. Start live=false; read labs/32_cost_quotas_scaling_and_drift/RUNBOOK.md.

"""Lab 32: Cost quotas scaling and drift. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import args,save,read
opts=args('Estimate scenario cost using explicitly entered rates')
c=read('config/cost_scenario.json')
input_tokens=c['requests']*c['calls_per_request']*c['input_tokens_per_call']
output_tokens=c['requests']*c['calls_per_request']*c['output_tokens_per_call']
cost=(input_tokens*c['input_price_per_million']+output_tokens*c['output_price_per_million'])/1e6
save('32_capacity.json',{'prices_are_user_supplied_examples':True,'currency':c['currency'],
 'estimated_token_cost':cost,'tokens':input_tokens+output_tokens,
 'idealized_minutes_at_quota':(input_tokens+output_tokens)/c['tokens_per_minute'],
 'excluded':'Search, storage, safety, observability, audio/image/video charges; bursts and service accounting differ.'})
