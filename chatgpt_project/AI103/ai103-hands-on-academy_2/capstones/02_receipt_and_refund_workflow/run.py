# Purpose: Combine receipt extraction and refund review
# Learn: Separate extracted claims from deterministic eligibility and a human-approved simulated effect.
# Run: Import databricks/capstones/02_receipt_and_refund_workflow.py as a Databricks source notebook. Start live=false; read capstones/02_receipt_and_refund_workflow/RUNBOOK.md.

"""Document extraction + deterministic eligibility + approval + idempotent simulated effect."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import args,save,ROOT,fixture
from academy.domain import Ledger,ALICE,SUPERVISOR
from academy.media import document
opts=args('Receipt/approval capstone; no real payment endpoint')
if opts.live and opts.variant == 'approve':
    raise ValueError('Live receipts require human field review. The approve fixture is offline only; use the Azure approval exercise.')
if opts.live:
    extracted=document(opts.file or ROOT/'data/media/receipt.png')
    # Inspect actual fields. Extraction is evidence, not authorization.
    totals=[]
    for d in extracted.get('documents',[]):
        value=d.get('fields',{}).get('Total',{})
        amount=value.get('valueCurrency',{}).get('amount',value.get('valueNumber'))
        if amount is not None:
            totals.append(amount)
    extraction={'totals':totals,'needs_human_field_review':True}
else:
    extraction=fixture('receipt')
db=Ledger(':memory:')
request=db.create('capstone-refund-001','ORD-1001',ALICE)
# The human role is a fixed test fixture, not an authenticated production approver.
review=db.decide(request['id'],SUPERVISOR,opts.variant=='approve')
if review['state']=='approved':
    final=db.execute(request['id'],ALICE)
    db.execute(request['id'],ALICE)
else:
    final=review
count=db.db.execute('SELECT COUNT(*) FROM effects').fetchone()[0]
save('capstone02.json',{'extraction':extraction,'request':request,'review':review,'final':final,
 'simulated_effects':count,'real_money_moved':False,'note':'Default variant rejects; variant=approve exercises the synthetic reviewer fixture.'})
db.close()
