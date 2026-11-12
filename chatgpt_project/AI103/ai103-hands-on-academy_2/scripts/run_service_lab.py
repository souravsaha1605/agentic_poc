"""Run selected academy labs in Cloud Shell without requiring Databricks.

Default is offline. --live sends synthetic inputs to the chosen Azure service.
Credentials are entered with a hidden prompt, kept in the child environment,
and never written to a .env file or placed in command arguments.
"""
import argparse
import getpass
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LABS = {
    'language': ('06_language_and_pii_preprocessing', 'language.txt', ('LANGUAGE_ENDPOINT', 'LANGUAGE_KEY')),
    'documents': ('25_document_intelligence_receipts_and_layout', 'documents.txt', ('DOCUMENT_ENDPOINT', 'DOCUMENT_KEY')),
    'translator': ('07_translation_and_multilingual_flow', 'core.txt', ('TRANSLATOR_ENDPOINT', 'TRANSLATOR_REGION', 'TRANSLATOR_KEY')),
    'speech': ('27_speech_transcription_synthesis_translation', 'speech.txt', ('SPEECH_REGION', 'SPEECH_KEY')),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('service', choices=LABS)
    parser.add_argument('--live', action='store_true')
    args = parser.parse_args()
    lab, requirements, names = LABS[args.service]
    child_env = os.environ.copy()
    child_env['PYTHONPATH'] = str(ROOT / 'src')
    child_env['ACADEMY_SKIP_DOTENV'] = 'true'
    child_env.setdefault('ACADEMY_OUTPUT_DIR', str(Path.cwd() / 'service-lab-evidence' / args.service))
    if args.live:
        print('Live Azure requests use credit. Install requirements/' + requirements + ' first.')
        for name in names:
            if child_env.get(name):
                continue
            if not sys.stdin.isatty():
                parser.error('Missing ' + name + '; use an interactive secure terminal or existing environment binding')
            if name.endswith('_KEY'):
                value = getpass.getpass(name + ' (hidden): ')
            else:
                value = input(name + ': ').strip()
            if not value:
                parser.error(name + ' cannot be empty')
            child_env[name] = value
    command = [sys.executable, str(ROOT / 'labs' / lab / 'run.py')]
    if args.live:
        command.append('--live')
    return subprocess.run(command, cwd=ROOT, env=child_env).returncode


if __name__ == '__main__':
    raise SystemExit(main())
