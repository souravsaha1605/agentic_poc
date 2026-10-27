# Purpose: Ground answers in enterprise data
# Learn: Separate synthetic evidence from authorized Fabric SQL and parameterized operational data access.
# Run: Import databricks/labs/30_enterprise_grounding_and_operational_data.py as a Databricks source notebook. Start live=false; read labs/30_enterprise_grounding_and_operational_data/RUNBOOK.md.

"""Lab 30: Enterprise grounding and operational data. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import args,save,env
opts=args('Compare operational and analytical grounding')
if opts.live and opts.variant=='fabric':
    import pyodbc
    with pyodbc.connect(env('FABRIC_SQL_CONNECTION_STRING'),timeout=15) as conn:
        cursor=conn.cursor()
        cursor.execute('SELECT TOP (10) product_id, units FROM dbo.ai103_sales WHERE region = ?',('IN',))
        result=[{'product_id':r[0],'units':r[1]} for r in cursor.fetchall()]
elif opts.live:
    raise ValueError('Use --variant fabric; Cosmos vector exercise is in cosmos_vector.py')
else:result={'question':'What sold well and is it available now?',
 'analytical_snapshot':[{'product_id':'K100','units_last_month':120}],
 'live_inventory':[{'product_id':'K100','stock_now':4}],
 'joined_answer':'K100 sold 120 units in the sample month and currently has 4 in stock.',
 'note':'Both datasets are synthetic; freshness timestamps must be tracked independently.'}
save('30_enterprise.json',result)
