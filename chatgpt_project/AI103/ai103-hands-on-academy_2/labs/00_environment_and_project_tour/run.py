# Purpose: Inspect the course environment
# Learn: Locate configuration, synthetic data and saved evidence before making service calls.
# Run: Import databricks/labs/00_environment_and_project_tour.py as a Databricks source notebook. Start live=false; read labs/00_environment_and_project_tour/RUNBOOK.md.

"""Lab 00: Environment and project tour. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import ROOT,args,save
import sys
opts=args('Verify the local environment')
assert sys.version_info >= (3,11), 'Python 3.11+ required'
save('00_environment.json',{'python':sys.version.split()[0],'root':str(ROOT),'cloud_called':False,
 'next':'Open lab 01 README; no Azure resource is needed for this check.'})
