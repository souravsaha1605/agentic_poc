# Purpose: Experiment with generation controls
# Learn: Change temperature or output budget one at a time; compare code generation without executing generated code.
# Run: Import databricks/extensions/03_generation_controls.py as a Databricks source notebook. Start live=false; read extensions/generation_controls/RUNBOOK.md.

"""Change ONE generation control, compare outputs, and retain usage evidence."""
from academy.common import args, env, save
from academy.cloud import chat
opts = args('Prompt and parameter experiment')
if opts.live:
    # Some reasoning models reject temperature; use a chat deployment that supports it.
    settings = {'max_completion_tokens': int(env('GENERATION_MAX_TOKENS', '256'))}
    if opts.variant == 'temperature':
        settings['temperature'] = float(env('GENERATION_TEMPERATURE', '0.2'))
    instruction = 'Write one sentence, then list evidence gaps. Do not invent facts.'
    if opts.variant == 'code':
        instruction = 'Explain Python code for summing a list; return code as text only. It will not be executed.'
    response = chat([{'role':'system','content':instruction},{'role':'user','content':opts.question}], **settings)
    result = {'settings':settings,'answer':response.choices[0].message.content,
              'usage':response.usage.model_dump() if response.usage else None}
else:
    result = {'mode':'configuration preview','max_completion_tokens':256,'temperature':'only for supporting deployments',
              'experiment':'Compare the same question with 0.2 and 0.8; do not assume deterministic output.'}
save('03_generation_controls.json', result)
