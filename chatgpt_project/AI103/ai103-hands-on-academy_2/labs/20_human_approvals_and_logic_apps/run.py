# Purpose: Require a human approval before an effect
# Learn: Inspect pending, approved, rejected and expired states; a simulated ledger is not a payment system.
# Run: Import databricks/labs/20_human_approvals_and_logic_apps.py as a Databricks source notebook. Start live=false; read labs/20_human_approvals_and_logic_apps/RUNBOOK.md.

"""Lab 20: Human approvals and Logic Apps. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import args,save
from academy.domain import Ledger,ALICE,SUPERVISOR
opts=args('Exercise an approval gate without any real financial action')
if opts.live:
    raise SystemExit('Use PORTAL.md for the Logic Apps integration. This script exercises the local state machine.')
db=Ledger(':memory:')
created=db.create('approval-demo','ORD-1001',ALICE)
try:
    db.execute('approval-demo',ALICE)
except PermissionError:
    before='blocked while pending'
decision=db.decide('approval-demo',SUPERVISOR,opts.variant!='reject')
if decision['state']=='approved':
    final=db.execute('approval-demo',ALICE)
else:
    final=decision
save('20_approval.json',{'created':created,'before_approval':before,'decision':decision,'final':final,'money_moved':False})
db.close()
