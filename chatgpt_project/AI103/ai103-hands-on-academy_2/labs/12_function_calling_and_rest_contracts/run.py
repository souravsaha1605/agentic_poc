# Purpose: Execute validated model tool requests
# Learn: Read a JSON tool schema, enforce permissions and return bounded tool results to the model.
# Run: Import databricks/labs/12_function_calling_and_rest_contracts.py as a Databricks source notebook. Start live=false; read labs/12_function_calling_and_rest_contracts/RUNBOOK.md.

"""Lab 12: Function calling and REST contracts. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import args,save
from academy.flows import agent
opts=args('Run a bounded tool loop with local read-only business tools')
save('12_tools.json',agent(opts.question,live=opts.live))
