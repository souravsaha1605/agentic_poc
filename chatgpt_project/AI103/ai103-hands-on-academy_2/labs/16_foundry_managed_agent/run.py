# Purpose: Create a managed Foundry agent
# Learn: Follow project identity, agent version creation, conversation state and response lifecycle.
# Run: Import databricks/labs/16_foundry_managed_agent.py as a Databricks source notebook. Start live=false; read labs/16_foundry_managed_agent/RUNBOOK.md.

"""Lab 16: Foundry managed agent. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import args,env,save
opts=args('Create one managed agent version and ask two questions')
if opts.live:
    from azure.identity import DefaultAzureCredential
    from azure.ai.projects import AIProjectClient
    from azure.ai.projects.models import PromptAgentDefinition
    project=AIProjectClient(endpoint=env('FOUNDRY_PROJECT_ENDPOINT'),credential=DefaultAzureCredential())
    name=env('FOUNDRY_AGENT_NAME','ai103-learning-agent')
    version=project.agents.create_version(agent_name=name,definition=PromptAgentDefinition(
      model=env('MODEL_SMALL'),instructions='You are a retail learning assistant. Do not execute transactions.'))
    client=project.get_openai_client(agent_name=name)
    conversation=client.conversations.create()
    try:
        first=client.responses.create(conversation=conversation.id,input='Remember: the product code is K100.')
        second=client.responses.create(conversation=conversation.id,input='What product code did I mention?')
        result={'agent':name,'version':version.version,'first':first.output_text,'second':second.output_text}
    finally:
        client.conversations.delete(conversation.id)
    # Keep the agent version so the learner can inspect its definition in Foundry.
else:
    result={'mode':'local plan only','create':'versioned prompt agent','state':'managed conversation','requires':'azure-ai-projects 2.x'}
save('16_foundry_agent.json',result)
