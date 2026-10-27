# Purpose: Handle a custom Search enrichment batch
# Learn: Preserve record IDs, emit product codes and report per-record errors using the custom skill contract.
# Run: Import databricks/extensions/10_custom_enrichment.py as a Databricks source notebook. Start live=false; read extensions/custom_skill/RUNBOOK.md.

"""Read academy.enrichment.enrich for the actual batch contract implementation."""
from academy.enrichment import enrich
if __name__ == '__main__':
    import json
    print(json.dumps(enrich({'values':[{'recordId':'1','data':{'text':'K100 kettle and K200 toaster'}}]}),indent=2))
