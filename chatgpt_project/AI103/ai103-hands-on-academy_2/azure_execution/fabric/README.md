# Fabric SQL fallback and exact connection settings

Fabric is a separate Microsoft portal with its own capacity/workspace permissions. Azure
subscription access alone is not sufficient. You can create/select Fabric capacity through
Azure Portal, then open Fabric for Lakehouse/table setup.

1. Complete [enterprise setup](../../docs/setup/06_MEMORY_AND_ENTERPRISE.md). Load the supplied
   CSV as table `dbo.ai103_sales`. In the SQL analytics endpoint, run:

```sql
SELECT TOP (10) product_id, units FROM dbo.ai103_sales WHERE region = 'IN';
```

Expect the synthetic India-region rows. This is the portal fallback when ODBC is unavailable.

2. For the Databricks Python path, confirm `import pyodbc; print(pyodbc.drivers())` includes
   `ODBC Driver 18 for SQL Server`. `%pip install pyodbc` installs the Python wrapper only.
3. Copy the server name and database from the endpoint's SQL connection details. Use an approved
   Entra service principal enabled by your Fabric tenant administrator and granted access to the
   item/SQL endpoint. Enable the service-principal tenant setting if your organization requires it.
4. In Key Vault secret `fabric-sql-connection-string`, store a connection string with this shape:

```text
Driver={ODBC Driver 18 for SQL Server};Server=tcp:YOUR_SQL_HOST,1433;Database=YOUR_SQL_DATABASE;Encrypt=yes;TrustServerCertificate=no;Authentication=ActiveDirectoryServicePrincipal;UID=YOUR_CLIENT_ID;PWD=YOUR_CLIENT_SECRET;
```

Populate it privately; do not paste the real string into notebooks or config_json. If your
approved identity method differs, use that method's documented connection string. Special
characters in values require ODBC escaping; use a dedicated secret appropriate to this driver.
5. Databricks lab 30: live=true, variant=fabric. If the driver is missing, use the SQL editor
   above or [the Azure VM fallback](../native_vm/README.md). Do not try a SQL password login
   against an Entra-only endpoint.
6. Save the query, row count, source time period and access-denied test as evidence. Delete the
   learning Lakehouse/capacity only when no other users depend on it.
