# Purpose: Smoke-test all notebook launchers with mock DBUtils
# Learn: Understand what a driver-only mock proves and what requires a real workspace.
# Run: From project root: python scripts/verify_notebooks.py. Expect 49/49 passed; no real Databricks runtime or live package install is used.

"""Local notebook smoke test with mocked DBUtils; NOT a real Databricks runtime test."""
import argparse
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import runpy
import shutil
import sys
import tempfile
import types
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[1]
# output_directory is mocked to a temporary directory; no real UC volume is mounted.
workspace = tempfile.TemporaryDirectory(prefix='ai103-notebooks-')
output = Path(workspace.name)
sys.path.insert(0,str(ROOT/'src'))
from academy import notebook as runtime
from unittest.mock import patch
output_patch = patch.object(runtime, 'output_directory', return_value=output)
output_patch.start()
class Widgets:
    def __init__(self):
        self.values={'project_root':str(ROOT),'output_root':'/Volumes/mock/catalog/volume/review','live':'false'}
    def text(self,name,default):
        self.values.setdefault(name,default)
    def dropdown(self,name,default,choices):
        self.values.setdefault(name,default)
    def get(self,name):
        return self.values[name]
parser = argparse.ArgumentParser(description='Mock Databricks launcher smoke tests')
parser.add_argument('--all-variants', action='store_true', help='Also execute every nondefault offline variant')
options = parser.parse_args()
catalog = json.loads((ROOT/'config/execution.json').read_text())
results=[]
try:
    for notebook in sorted((ROOT/'databricks').glob('*/*.py')):
        entry = str(notebook.relative_to(ROOT/'databricks').with_suffix(''))
        variants = catalog[entry]['variants'] if options.all_variants else ['default']
        for variant in variants:
            widgets=Widgets()
            widgets.values['variant'] = variant
            def denied(**kwargs):
                raise AssertionError('Offline path requested a secret')
            mock=types.SimpleNamespace(widgets=widgets,secrets=types.SimpleNamespace(get=denied),
                                       library=types.SimpleNamespace(restartPython=lambda:None))
            try:
                with redirect_stdout(io.StringIO()):
                    runpy.run_path(str(notebook),init_globals={'dbutils':mock})
                results.append({'notebook':str(notebook.relative_to(ROOT)),'variant':variant,'passed':True})
            except Exception as error:
                results.append({'notebook':str(notebook.relative_to(ROOT)),'variant':variant,'passed':False,'error':str(error)})
    print(json.dumps({'passed':sum(x['passed'] for x in results),'total':len(results),'results':results},indent=2))
finally:
    output_patch.stop()
    workspace.cleanup()
if not all(x['passed'] for x in results):
    raise SystemExit(1)
