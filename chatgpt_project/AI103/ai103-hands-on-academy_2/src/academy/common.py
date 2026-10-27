# Purpose: Provide shared inputs, configuration and evidence helpers
# Learn: Follow command arguments, environment access, fixtures, async execution and JSON evidence output.
# Run: Imported by lesson code; do not run this file directly. Follow the importing lesson in MASTER_GUIDE.md.

"""Small shared mechanics. Read a lab's run.py first, then follow imports here."""
import argparse
import json
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.getenv('ACADEMY_OUTPUT_DIR', str(ROOT / 'outputs'))) 

def load_env():
    """Load optional terminal configuration; Databricks explicitly disables .env."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return  # Offline labs require no optional dependencies.
    if os.getenv('ACADEMY_SKIP_DOTENV') != 'true':
        load_dotenv(ROOT / '.env', override=False)

def env(name, default=None):
    """Read one required setting and stop with setup guidance when it is missing."""
    load_env()
    value = os.getenv(name, default)
    if value is None or value == '' or str(value).startswith('YOUR_'):
        raise ValueError(f'Missing {name}: in Databricks add secret {name.lower().replace(chr(95), chr(45))} to the configured scope; locally set .env. See this lesson RUNBOOK.md.')
    return value

def args(description):
    """Parse the same options used by terminal commands and Databricks widgets."""
    p=argparse.ArgumentParser(description=description)
    p.add_argument('--live', action='store_true', help='Opt in to Azure calls, charges and lab resource changes')
    p.add_argument('--question', default='What is the return policy?')
    p.add_argument('--file', type=Path)
    p.add_argument('--variant', default='default')
    return p.parse_args()

def save(name, value):
    """Persist and print a result within the configured output directory."""
    OUT.mkdir(parents=True, exist_ok=True)
    p=OUT / name
    if not p.resolve().is_relative_to(OUT.resolve()):
        raise ValueError('Output name must stay within ACADEMY_OUTPUT_DIR')
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,indent=2,ensure_ascii=False,default=str),encoding='utf-8')
    print(json.dumps(value,indent=2,ensure_ascii=False,default=str))
    return p

def read(name):
    """Read bundled synthetic JSON relative to the project root."""
    return json.loads((ROOT / name).read_text(encoding='utf-8'))

def fixture(name):
    """Label fixed demonstration data so it cannot be mistaken for a service response."""
    return {'execution':'OFFLINE_FIXTURE — no Azure/model call', 'result':read('data/fixtures/'+name+'.json')}


def run_async(coroutine):
    """Works in a terminal and inside Databricks' already-running event loop."""
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coroutine)
    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coroutine).result()
