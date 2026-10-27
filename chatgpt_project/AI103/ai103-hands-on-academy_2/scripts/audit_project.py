# Purpose: Audit source syntax and internal file references
# Learn: Understand the difference between a static audit and live service verification.
# Run: From project root: python scripts/audit_project.py. Inspect errors=[]; this does not validate Bicep deployment or SDK compatibility.

"""Validate every packaged text/code path without requiring cloud packages."""
import ast
import hashlib
import json
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]
counts={}
for path in sorted(ROOT.rglob('*')):
    if not path.is_file() or '__pycache__' in path.parts or 'outputs' in path.parts:
        continue
    ext=path.suffix
    counts[ext]=counts.get(ext,0)+1
    try:
        if ext=='.py':ast.parse(path.read_text(encoding='utf-8'))
        elif ext=='.json':json.loads(path.read_text(encoding='utf-8'))
        elif ext=='.md':
            for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
                if '://' in link or link.startswith(('#','mailto:')):continue
                target=link.split('#')[0]
                if target and not (path.parent/target).exists():errors.append(str(path.relative_to(ROOT))+': '+target)
    except (ValueError,SyntaxError) as error:errors.append(str(path.relative_to(ROOT))+': '+str(error))
for requirement in (ROOT/'requirements').glob('*.txt'):
    for line in requirement.read_text().splitlines():
        if line.startswith('-r ') and not (requirement.parent/line[3:].strip()).is_file():
            errors.append('Missing requirement include: '+str(requirement))
catalog=json.loads((ROOT/'config/execution.json').read_text())
for entry,spec in catalog.items():
    for relative in (spec['target'],spec['requirements'],'databricks/'+entry+'.py',str(Path(spec['target']).parent/'RUNBOOK.md')):
        if not (ROOT/relative).is_file():errors.append('Missing catalog target: '+relative)
try:
    import yaml
    for path in (ROOT/'.github/workflows').glob('*.yml'):yaml.safe_load(path.read_text())
    yaml_status='parsed with PyYAML; not a hosted workflow test'
except ImportError:yaml_status='not checked: optional PyYAML unavailable'
print(json.dumps({'counts_by_extension':counts,'catalog_entries':len(catalog),'yaml':yaml_status,'errors':errors},indent=2))
if errors:raise SystemExit(1)
