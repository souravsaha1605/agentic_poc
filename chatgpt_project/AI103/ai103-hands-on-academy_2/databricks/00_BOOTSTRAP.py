# Databricks notebook source
# MAGIC %md
# MAGIC **Purpose:** Extract the course safely onto the Databricks driver
# MAGIC **Learn:** Distinguish temporary driver code from durable Unity Catalog output; reject unsafe ZIP paths.
# MAGIC **Run:** Import this source notebook into Databricks. Set zip_path and output_root to your volume paths; run first and after compute restarts. It replaces the temporary extracted course copy.

# COMMAND ----------
# MAGIC %md
# MAGIC # Prepare the incremental AI-103 course
# MAGIC Read `docs/setup/DATABRICKS.md` first. Upload the course ZIP to a Unity Catalog volume.
# MAGIC This notebook extracts code to the driver. Outputs go to your volume. No Azure service calls.

# COMMAND ----------
dbutils.widgets.text('zip_path','/Volumes/YOUR_CATALOG/YOUR_SCHEMA/YOUR_VOLUME/ai103-hands-on-academy.zip')
dbutils.widgets.text('output_root','/Volumes/YOUR_CATALOG/YOUR_SCHEMA/YOUR_VOLUME/ai103-output')

# COMMAND ----------
from pathlib import Path
import zipfile
import shutil
import tempfile
zip_path=Path(dbutils.widgets.get('zip_path'))
output_root=Path(dbutils.widgets.get('output_root'))
assert zip_path.is_file(), 'Upload the ZIP and set zip_path first'
assert (str(output_root).startswith('/Volumes/') and len(output_root.parts) >= 5
        and '..' not in output_root.parts and 'YOUR_' not in str(output_root)), \
    'Set a writable /Volumes/catalog/schema/volume/output path without traversal'
local_parent=Path('/local_disk0/tmp/ai103-course')
local_parent.mkdir(parents=True,exist_ok=True)
# Your edits belong in Workspace/Git. This replaces only the temporary course driver copy.
project_root = local_parent/'ai103-hands-on-academy'
with zipfile.ZipFile(zip_path) as archive:
    # Prevent path traversal if you substitute another archive later.
    for member in archive.infolist():
        dest=(local_parent/member.filename).resolve()
        if not dest.is_relative_to(local_parent.resolve()):
            raise ValueError('Archive contains an unsafe path')
    if any(not m.filename.startswith('ai103-hands-on-academy/') for m in archive.infolist()):
        raise ValueError('Expected exactly the course top-level folder')
    with tempfile.TemporaryDirectory(dir=local_parent) as staging:
        archive.extractall(staging)
        staged = Path(staging)/'ai103-hands-on-academy'
        assert (staged/'src/academy/notebook.py').is_file(), 'ZIP is missing reviewed launcher code'
        if project_root.exists():
            shutil.rmtree(project_root)
        shutil.move(str(staged), str(project_root))
project_root=local_parent/'ai103-hands-on-academy'
assert (project_root/'src/academy/common.py').exists()
output_root.mkdir(parents=True,exist_ok=True)
print('project_root:',project_root)
print('output_root:',output_root)
print('Import a single lesson notebook from databricks/labs. Set these widget values there.')

# COMMAND ----------
# MAGIC %md
# MAGIC The driver folder is temporary. After compute restarts, rerun this bootstrap.
# MAGIC Save experiments as separate workspace notebooks or commit changes to a Git folder.
# MAGIC Do not store keys in notebooks, the ZIP, widgets, printed output, or Spark configuration.
