# Databricks notebook source
# MAGIC %md
# MAGIC **Purpose:** Launch: Build an enterprise research assistant
# MAGIC **Learn:** Combine authorized evidence, parallel retrieval and bounded review; compare synthetic analytics with Fabric.
# MAGIC **Run:** Import databricks/capstones/04_enterprise_research_assistant.py as a Databricks source notebook. Start live=false; read capstones/04_enterprise_research_assistant/RUNBOOK.md. Execute cells in order; after a live package install, restart Python once then run the final cell.

# COMMAND ----------
# MAGIC %md
# MAGIC # 04 enterprise research assistant
# MAGIC Read `capstones/04_enterprise_research_assistant/RUNBOOK.md` in the extracted ZIP before running.
# MAGIC This notebook runs **one lesson**. Start with `live=false` (no Azure AI charges).
# MAGIC Databricks compute itself can incur charges. Run bootstrap after compute restarts.

# COMMAND ----------
# Step 1: fill these visible widgets. Never put credentials in widget values.
dbutils.widgets.text('project_root','/local_disk0/tmp/ai103-course/ai103-hands-on-academy')
dbutils.widgets.text('output_root','/Volumes/YOUR_CATALOG/YOUR_SCHEMA/YOUR_VOLUME/ai103-output')
dbutils.widgets.text('secret_scope','ai103-lab')
dbutils.widgets.dropdown('live','false',['false','true'])
dbutils.widgets.dropdown('variant','default',['default', 'fabric'])
dbutils.widgets.text('question','What is the return policy?')
dbutils.widgets.text('input_file','')
dbutils.widgets.text('config_json','{}')

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 2 — validate settings and install only this lesson's packages
# MAGIC Keep this cell separate from the execution cell. No Azure service call happens here.
# MAGIC If pip fails, stop and fix the install before proceeding; see TROUBLESHOOTING.md.

# COMMAND ----------
from pathlib import Path
import sys
project_root = Path(dbutils.widgets.get('project_root'))
assert sys.version_info >= (3,11), 'Select compute with Python 3.11 or newer'
assert (project_root/'src/academy/notebook.py').exists(), 'Rerun bootstrap using the reviewed ZIP'
sys.path.insert(0,str(project_root/'src'))
from academy.notebook import validate_variant, configuration
import json
spec = json.loads((project_root/'config/execution.json').read_text())['capstones/04_enterprise_research_assistant']
validate_variant('capstones/04_enterprise_research_assistant', spec, dbutils.widgets.get('variant'), dbutils.widgets.get('live')=='true')
configuration(dbutils.widgets.get('config_json'))
if dbutils.widgets.get('live') == 'true':
    requirements = project_root/'requirements/enterprise.txt'
    get_ipython().run_line_magic('pip', f'install -r "{requirements}"')

# COMMAND ----------
# Step 3: Python restart is required after package changes. Widgets survive it.
# Once it finishes, run the final cell below; do not rerun the restart cell in a loop.
if dbutils.widgets.get('live') == 'true':
    dbutils.library.restartPython()

# COMMAND ----------
# Step 4: the runner loads scope secrets, runs the lesson, saves evidence, then clears secrets.
import sys
from pathlib import Path
project_root = Path(dbutils.widgets.get('project_root'))
sys.path.insert(0,str(project_root/'src'))
from academy.notebook import run
run(dbutils, project_root, 'capstones/04_enterprise_research_assistant')
