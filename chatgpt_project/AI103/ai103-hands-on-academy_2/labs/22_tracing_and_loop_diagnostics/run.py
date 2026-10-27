# Purpose: Trace workflow execution
# Learn: Inspect spans, latency and loop diagnostics without logging secrets or sensitive prompts.
# Run: Import databricks/labs/22_tracing_and_loop_diagnostics.py as a Databricks source notebook. Start live=false; read labs/22_tracing_and_loop_diagnostics/RUNBOOK.md.

"""Lab 22: Tracing and loop diagnostics. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
import time,uuid
from academy.common import args,save,env
from academy.domain import retrieve
opts=args('Create a trace with a retrieval child span')
if opts.live:
    from azure.monitor.opentelemetry import configure_azure_monitor
    from opentelemetry import trace
    configure_azure_monitor(connection_string=env('APPLICATIONINSIGHTS_CONNECTION_STRING'))
    tracer=trace.get_tracer('ai103-academy')
    with tracer.start_as_current_span('support.request') as parent:
        parent.set_attribute('lab.id','22')
        with tracer.start_as_current_span('retrieval.search') as child:
            hits=retrieve(opts.question)
            child.set_attribute('retrieval.count',len(hits))
    flushed = trace.get_tracer_provider().force_flush()
    result={'export_flush_completed':flushed,'ingestion_verified':False,'inspect':'Application Insights transaction search; filter lab.id=22'}
else:
    trace_id=uuid.uuid4().hex
    start=time.perf_counter()
    hits=retrieve(opts.question)
    result={'mode':'local trace-shaped record, NOT OpenTelemetry export','trace_id':trace_id,
      'spans':[{'name':'retrieval.search','duration_ms':(time.perf_counter()-start)*1000,'count':len(hits)}]}
save('22_trace.json',result)
