# Purpose: Execute all main lessons and capstones offline
# Learn: Check deterministic examples without installing Azure SDKs.
# Run: From project root: python scripts/verify_offline.py. Expect 37/37 passed; temporary results are deleted.

"""Run every local lesson/capstone. No Azure calls or optional SDK installs."""
from pathlib import Path
import json,os,subprocess,sys,tempfile
root=Path(__file__).resolve().parents[1]
files=sorted(root.glob('labs/*/run.py'))+sorted(root.glob('capstones/*/run.py'))
results=[]
with tempfile.TemporaryDirectory() as tmp:
    env=os.environ.copy()
    env['PYTHONPATH']=str(root/'src')
    env['ACADEMY_OUTPUT_DIR']=tmp
    for p in files:
        r=subprocess.run([sys.executable,str(p)],cwd=root,env=env,capture_output=True,text=True,timeout=45)
        results.append({'script':str(p.relative_to(root)),'passed':r.returncode==0})
        if r.returncode:
            print(r.stderr)
            print(r.stdout)
print(json.dumps({'passed':sum(x['passed'] for x in results),'total':len(results),'results':results},indent=2))
if not all(x['passed'] for x in results):
    raise SystemExit(1)
