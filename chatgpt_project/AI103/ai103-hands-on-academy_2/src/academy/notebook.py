# Purpose: Bridge Databricks widgets to lesson entrypoints
# Learn: Understand secret loading, variant checks, unique output folders, temporary input staging and cleanup.
# Run: Imported by lesson code; do not run this file directly. Follow the importing lesson in MASTER_GUIDE.md.

"""Databricks launch mechanics, separated from the AI lesson itself.

Keep all service calls on the driver. Never serialize clients or credentials into Spark.
The public helpers also make notebook configuration testable without a paid workspace.
"""
import importlib.metadata
import json
import os
from pathlib import Path
import runpy
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from uuid import uuid4

# Widget overrides are non-secret only. They reset on EVERY execution.
DEFAULTS = {
    'MODEL_AUTH': 'key', 'SEARCH_INDEX': 'ai103-policies-v1',
    'CU_ANALYZER': 'prebuilt-invoice', 'CU_API_VERSION': '2025-11-01',
    'IMAGE_API_VERSION': '2025-04-01-preview', 'SPEECH_LANGUAGE': 'en-US',
    'SPEECH_VOICE': 'en-US-AvaMultilingualNeural',
    'COSMOS_DATABASE': 'ai103', 'COSMOS_CONTAINER': 'memory',
    'TRANSLATOR_ENDPOINT': 'https://api.cognitive.microsofttranslator.com',
    'VIDEO_SIZE': '1280x720', 'VIDEO_SECONDS': '4',
    'FOUNDRY_AGENT_NAME': 'ai103-learning-agent',
}
OPTIONAL = {'CU_COMPLETION_MODEL', 'VIDEO_ID', 'DOCUMENT_MODEL_ID', 'GENERATION_TEMPERATURE', 'GENERATION_MAX_TOKENS'}
IDENTITY = ['AZURE_TENANT_ID', 'AZURE_CLIENT_ID', 'AZURE_CLIENT_SECRET']


def configuration(raw):
    """Parse settings without allowing credentials to be placed in visible widgets."""
    try:
        supplied = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError('config_json must be valid JSON, for example {"SEARCH_INDEX":"ai103-policies-v1"}') from None
    if not isinstance(supplied, dict) or not set(supplied) <= set(DEFAULTS) | OPTIONAL:
        raise ValueError('Unknown config_json name; see docs/CONFIGURATION.md for allowed settings')
    if not all(isinstance(value, str) for value in supplied.values()):
        raise ValueError('Every config_json value must be a quoted string')
    result = {**DEFAULTS, **supplied}
    if result['MODEL_AUTH'] not in ('key', 'entra'):
        raise ValueError('MODEL_AUTH must be key or entra')
    return result


def required_secrets(entry_id, spec, variant, settings):
    """Select the minimum credentials for the actual branch being executed."""
    names = list(spec['required'])
    if entry_id.startswith('capstones/03_') and variant == 'speech':
        names += ['SPEECH_KEY', 'SPEECH_REGION']
    if entry_id.startswith('capstones/04_') and variant == 'fabric':
        names += ['FABRIC_SQL_CONNECTION_STRING']
    if entry_id.startswith('labs/15_'):
        names = ['REDIS_URL'] if variant == 'redis' else IDENTITY + ['COSMOS_ENDPOINT']
    if entry_id.startswith('labs/27_') and variant == 'custom':
        names += ['SPEECH_CUSTOM_ENDPOINT_ID']
    if entry_id.startswith('labs/17_') and variant == 'azure-search':
        names += ['MODEL_EMBEDDING', 'SEARCH_ENDPOINT', 'SEARCH_ADMIN_KEY']
    if settings['MODEL_AUTH'] == 'entra' and 'AZURE_OPENAI_ENDPOINT' in names:
        if spec.get('key_only'):
            raise ValueError('This lesson adapter uses a key. Set MODEL_AUTH=key for this lesson.')
        names = [n for n in names if n != 'AZURE_OPENAI_API_KEY'] + IDENTITY
    return sorted(set(names))


def validate_variant(entry_id, spec, variant, live):
    if variant not in spec['variants']:
        raise ValueError('variant must be one of: ' + ', '.join(spec['variants']))
    if live and spec['kind'] in ('local', 'portal'):
        raise ValueError('Keep live=false for this notebook. For the service exercise open azure_execution/README.md.')
    if live and (entry_id.startswith('labs/15_') or entry_id.startswith('labs/30_')) and variant == 'default':
        raise ValueError('Choose a live variant from this lesson RUNBOOK.md before running')


def output_directory(raw):
    """Require a learner-owned UC volume; tests substitute this boundary, not a real mount."""
    parts = Path(raw).parts
    if (not raw.startswith('/Volumes/') or 'YOUR_' in raw
            or '..' in parts or len(parts) < 5):
        raise ValueError('Replace output_root with your writable /Volumes/catalog/schema/volume/ai103-output path')
    return Path(raw)


def run(dbutils, project_root, entry_id):
    """Execute one lesson with clean configuration and a unique evidence directory."""
    root = Path(project_root).resolve()
    catalog = json.loads((root / 'config/execution.json').read_text())
    spec = catalog[entry_id]
    live = dbutils.widgets.get('live') == 'true'
    variant = dbutils.widgets.get('variant')
    validate_variant(entry_id, spec, variant, live)
    settings = configuration(dbutils.widgets.get('config_json'))
    if live and entry_id.startswith('capstones/02_') and variant == 'approve':
        raise ValueError('approve is a synthetic offline fixture. Use the documented Azure human review workflow for live receipts.')
    if live and entry_id.startswith('capstones/03_') and variant == 'speech' and not dbutils.widgets.get('input_file'):
        raise ValueError('Speech variant needs a short WAV in input_file; start with lab 27 sample.wav.')
    if live and variant in ('resume', 'remix') and 'VIDEO_ID' not in settings:
        raise ValueError('Add VIDEO_ID to config_json using the prior video_job.json ID')
    if live and variant == 'custom' and entry_id.startswith('labs/25_') and 'DOCUMENT_MODEL_ID' not in settings:
        raise ValueError('Add DOCUMENT_MODEL_ID from Document Intelligence Studio to config_json')
    output_root = output_directory(dbutils.widgets.get('output_root'))
    # Every execution has its own folder; a failed run cannot masquerade as an older result.
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid4().hex[:6]
    output = output_root / entry_id.replace('/', '-') / stamp
    output.mkdir(parents=True, exist_ok=False)
    managed = set(DEFAULTS) | OPTIONAL | set(IDENTITY) | {'REDIS_URL','COSMOS_ENDPOINT','SPEECH_CUSTOM_ENDPOINT_ID'}
    for item in catalog.values():
        managed.update(item['required'])
    for name in managed:
        os.environ.pop(name, None)
    os.environ.update(settings)
    previous_runtime = {name: os.environ.get(name) for name in
                        ('ACADEMY_SKIP_DOTENV', 'ACADEMY_OUTPUT_DIR')}
    os.environ['ACADEMY_SKIP_DOTENV'] = 'true'
    os.environ['ACADEMY_OUTPUT_DIR'] = str(output)
    src = str(root / 'src')
    if src not in sys.path:
        sys.path.insert(0, src)
    old_pythonpath = os.environ.get('PYTHONPATH')
    os.environ['PYTHONPATH'] = src + (os.pathsep + old_pythonpath if old_pythonpath else '')
    # Common.OUT is evaluated at import time, so clear old lesson imports first.
    for name in list(sys.modules):
        if name.startswith('academy.') and name != __name__:
            del sys.modules[name]
    old_argv = sys.argv
    try:
        missing = []
        if live:
            scope = dbutils.widgets.get('secret_scope')
            for name in required_secrets(entry_id, spec, variant, settings):
                key = name.lower().replace('_', '-')
                try:
                    value = dbutils.secrets.get(scope=scope, key=key)
                    if not value or value.startswith('YOUR_'):
                        raise ValueError('empty')
                    os.environ[name] = value
                except Exception:
                    missing.append(key)
            if missing:
                raise ValueError('Missing or unreadable scope keys: ' + ', '.join(missing) + '. See this lesson RUNBOOK.md; secret values were not printed.')
        # Stage files for native clients, and clean temporary data after execution.
        with tempfile.TemporaryDirectory(prefix='ai103-input-') as stage:
            argv = [str(root / spec['target']), '--question', dbutils.widgets.get('question'), '--variant', variant]
            if live:
                argv.append('--live')
            input_file = dbutils.widgets.get('input_file')
            if input_file:
                source = Path(input_file)
                if not source.is_file():
                    raise ValueError('input_file does not exist; upload media to your volume and copy its full path')
                local = Path(stage) / source.name
                shutil.copyfile(source, local)
                argv += ['--file', str(local)]
            sys.argv = argv
            runpy.run_path(argv[0], run_name='__main__')
        packages = {d.metadata['Name']: d.version for d in importlib.metadata.distributions() if d.metadata['Name']}
        (output / 'environment.json').write_text(json.dumps({'python': sys.version.split()[0], 'packages': packages}, indent=2))
        (output / 'run_status.json').write_text(json.dumps({'entry':entry_id,'live':live,'variant':variant,'status':'completed'}, indent=2))
        print('Evidence saved in:', output)
    except BaseException as error:
        # Save type only: SDK exception text can contain request information.
        (output / 'run_status.json').write_text(json.dumps({'entry':entry_id,'live':live,'variant':variant,'status':'failed','error_type':type(error).__name__}, indent=2))
        print('Failure recorded in:', output)
        raise
    finally:
        sys.argv = old_argv
        for name, value in previous_runtime.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
        for name in managed:
            os.environ.pop(name, None)
        if old_pythonpath is None:
            os.environ.pop('PYTHONPATH', None)
        else:
            os.environ['PYTHONPATH'] = old_pythonpath
