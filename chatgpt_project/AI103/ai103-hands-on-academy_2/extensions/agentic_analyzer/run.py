# Purpose: Explore an agentic document analyzer preview
# Learn: Distinguish analyzer creation from analysis and understand preview access, model mappings and quota prerequisites.
# Run: Import databricks/extensions/26_agentic_analyzer.py as a Databricks source notebook. Start live=false; read extensions/agentic_analyzer/RUNBOOK.md.

"""Create a dedicated preview document analyzer, then analyze a synthetic receipt."""
from urllib.parse import quote
from academy.common import args, env, ROOT, read, save
from academy.cloud import request, cognitive_headers, poll_operation
from academy.media import understand
opts = args('Current migration exercise for retired pro mode')
if opts.live:
    if env('CU_API_VERSION') != '2026-06-01-preview':
        raise ValueError('This extension needs CU_API_VERSION=2026-06-01-preview; keep GA for lab 26')
    name = env('CU_ANALYZER')
    if not name.startswith('ai103-'):
        raise ValueError('Choose a dedicated analyzer ID starting ai103-; do not overwrite a prebuilt analyzer')
    if opts.variant == 'create':
        body = read('extensions/agentic_analyzer/analyzer.json')
        # This is a supported model family name mapped to a deployment in CU Settings.
        body['models'] = {'completion':env('CU_COMPLETION_MODEL')}
        endpoint = env('CU_ENDPOINT').rstrip('/')
        response = request('PUT', endpoint+'/contentunderstanding/analyzers/'+quote(name,safe='')+'?api-version=2026-06-01-preview',
                           headers=cognitive_headers('CU'), body=body)
        operation = response.headers.get('Operation-Location')
        if operation:
            poll_operation(operation,endpoint,'CU')
        result = {'analyzer_created':name,'next':'Run variant=default with the same config_json'}
    else:
        result = understand(opts.file or ROOT/'data/media/receipt.png', name)
else:
    result = {'mode':'schema preview','analyzer':read('extensions/agentic_analyzer/analyzer.json'),
              'note':'Historical pro API is retired; this exercise uses the current document-only preview.'}
save('26_agentic_analyzer.json',result)
