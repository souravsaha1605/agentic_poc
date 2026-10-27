# Exercises executed by Azure services or outside a Databricks notebook

The default for lesson Python code is **Databricks classic dedicated compute**.
This folder names the exceptions; they are not hidden inside a notebook.
All resource setup starts in Azure Portal. Azure Portal opens separate product studios for
Foundry, Speech, Document Intelligence, Databricks and Fabric. Those UIs are necessary;
there is no promise that every operation is an Azure Portal blade.
Commands below run in **Azure Cloud Shell**, which opens from the `>_` toolbar in Azure Portal.
You do not need Azure CLI installed on your computer. Cloud Shell commands are not notebook cells.

| Exercise | Actual runtime | Start here | Databricks role |
|---|---|---|---|
| App API and custom skill hosting | Azure App Service | [App hosting](app_service/README.md) | Call the hosted API after deployment |
| Indexer, OCR and enrichment | Azure AI Search service | [Search](search_indexer/README.md) | Query the resulting index |
| Human approval connector | Stateful Logic App | [Approvals](logic_apps/README.md) | Optional submit client; review decision in Azure |
| Infrastructure build, what-if, deployment, Cosmos roles | Azure Cloud Shell | [Cloud Shell](cloud_shell/README.md) | No infrastructure shell commands in notebooks |
| Speech native or MCP blocked by cluster policy | Azure Linux VM | [Native fallback](native_vm/README.md) | Use Databricks first; fallback only when blocked |
| Fabric ODBC driver unavailable | Fabric SQL editor or Azure VM | [Fabric](fabric/README.md) | Optional ODBC query if driver exists |
| Advanced Content Understanding / historical pro mode | CU Studio + Databricks REST | [Analyzer modes](content_understanding/README.md) | Submit supported analyzer requests |
| CI/CD | GitHub Actions hosted runner | [CI/CD](ci_cd/README.md) | Execute lessons and inspect outputs |

Do not mark a portal workflow verified merely because its matching notebook preview ran.
For every row capture the service run ID, result, one failure case, and cleanup action.
