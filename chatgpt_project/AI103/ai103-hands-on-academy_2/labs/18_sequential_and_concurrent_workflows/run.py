# Purpose: Compare sequential and concurrent workflows
# Learn: Measure independent tasks and inspect partial failure without treating parallel execution as reasoning.
# Run: Import databricks/labs/18_sequential_and_concurrent_workflows.py as a Databricks source notebook. Start live=false; read labs/18_sequential_and_concurrent_workflows/RUNBOOK.md.

"""Lab 18: Sequential and concurrent workflows. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import run_async
import asyncio,time
from academy.common import args,save
opts=args('Measure sequential and concurrent independent tasks')
async def read_source(name,delay,fail=False):
    await asyncio.sleep(delay)
    if fail:
        raise RuntimeError(name+' unavailable')
    return {'source':name,'status':'ok'}
async def main():
    start=time.perf_counter()
    serial=[await read_source('orders',.02),await read_source('policy',.03)]
    serial_ms=(time.perf_counter()-start)*1000
    start=time.perf_counter()
    parallel=await asyncio.gather(read_source('orders',.02),read_source('policy',.03,opts.variant=='failure'),return_exceptions=True)
    return {'sequential_ms':round(serial_ms,2),'concurrent_ms':round((time.perf_counter()-start)*1000,2),
      'results':[{'error':str(r)} if isinstance(r,Exception) else r for r in parallel]}
save('18_concurrency.json',run_async(main()))
