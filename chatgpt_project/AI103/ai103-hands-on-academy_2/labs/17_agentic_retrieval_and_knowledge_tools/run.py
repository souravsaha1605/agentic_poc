# Purpose: Connect retrieval to an agent tool
# Learn: Compare the synthetic policy backend with the Azure Search variant without dropping authorization.
# Run: Import databricks/labs/17_agentic_retrieval_and_knowledge_tools.py as a Databricks source notebook. Start live=false; read labs/17_agentic_retrieval_and_knowledge_tools/RUNBOOK.md.

"""Lab 17: Agentic retrieval and knowledge tools. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import args,save
from academy.flows import agent
opts=args('Observe when the model searches')
# Azure Search is selected by configuration, never by a model-provided URL or tenant.
from academy.search import search
backend = search if opts.live and opts.variant == 'azure-search' else None
save('17_agentic_rag.json',agent(opts.question,live=opts.live,policy_search=backend))
