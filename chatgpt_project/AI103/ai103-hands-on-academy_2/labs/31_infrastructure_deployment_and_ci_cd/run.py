# Purpose: Prepare deployment and infrastructure
# Learn: Read the Bicep, API packaging and CI/CD path; deploy resources only through the separate Azure instructions.
# Run: Import databricks/labs/31_infrastructure_deployment_and_ci_cd.py as a Databricks source notebook. Start live=false; read labs/31_infrastructure_deployment_and_ci_cd/RUNBOOK.md.

"""Lab 31: Infrastructure deployment and CI CD. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import args,ROOT,save
opts=args('Inspect deployment artifacts before running the documented CLI steps')
if opts.live:
    raise SystemExit('Follow PORTAL.md and infra/README.md for explicit resource deployment commands.')
files=['infra/main.bicep','.github/workflows/ci.yml','Dockerfile','src/academy/api.py']
save('31_deployment.json',{'artifacts':{f:(ROOT/f).exists() for f in files},
 'next':'Run local tests, then Bicep what-if, inspect changes, deploy, assign identity roles, smoke-test and roll back if needed.'})
