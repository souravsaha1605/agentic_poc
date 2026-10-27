# Purpose: Read authorized Fabric analytics
# Learn: Inspect a parameterized SQL query and native ODBC prerequisite; retrieval time is not data freshness.
# Run: Imported by lesson code; do not run this file directly. Follow the importing lesson in MASTER_GUIDE.md.

"""Read a small, authorized analytical slice with a parameterized SQL query."""
from datetime import datetime, timezone
from .common import env


def sales(region='IN'):
    import pyodbc
    if 'ODBC Driver 18 for SQL Server' not in pyodbc.drivers():
        raise RuntimeError('Native ODBC Driver 18 is missing; see azure_execution/fabric/README.md')
    with pyodbc.connect(env('FABRIC_SQL_CONNECTION_STRING'),timeout=15) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT TOP (10) product_id, units FROM dbo.ai103_sales WHERE region = ?', (region,))
        rows = [{'product_id':row[0],'units':row[1]} for row in cursor.fetchall()]
    return {'source':'Fabric SQL analytics endpoint','retrieved_at':datetime.now(timezone.utc).isoformat(),
            'rows':rows,'freshness_note':'Retrieval time is not the business period; inspect the source table period separately.'}
