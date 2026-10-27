# Purpose: Control retries, duplicates and caching
# Learn: Understand retry limits, idempotency keys, approval state and identity-aware cache isolation.
# Run: Import databricks/labs/14_retries_idempotency_and_caching.py as a Databricks source notebook. Start live=false; read labs/14_retries_idempotency_and_caching/RUNBOOK.md.

"""Lab 14: Retries idempotency and caching. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import args,save
from academy.domain import Ledger,ALICE,SUPERVISOR,TTLCache
opts=args('Retry the same simulated refund and inspect effects')
ledger=Ledger(':memory:')
ledger.create('req-001','ORD-1001',ALICE)
ledger.decide('req-001',SUPERVISOR,True)
a=ledger.execute('req-001',ALICE)
b=ledger.execute('req-001',ALICE)
count=ledger.db.execute('SELECT COUNT(*) FROM effects').fetchone()[0]
cache=TTLCache()
key=cache.key(ALICE,'returns','v1')
cache.put(key,'30 days',60)
save('14_reliability.json',{'first':a['state'],'retry':b['state'],'simulated_effect_count':count,'cache_hit':cache.get(key)})
ledger.close()
