# Azure AI Search and enrichment setup

## Small vector index through code

1. Azure Portal → Azure AI Search → Create. Use a dedicated learning service and supported tier.
   Some tiers/features have limits; semantic ranking can require enabling a billed feature.
2. Copy the search URL and an admin key into SEARCH_ENDPOINT/SEARCH_ADMIN_KEY. The starter
   uses the admin key to create and load an index. A production query path should use a narrower
   credential/role, not an index-management key.
3. In Foundry deploy a text embedding model and set MODEL_EMBEDDING. Verify you can call it.
4. Run lab 09 with live=true, variant=ingest. It creates/updates only SEARCH_INDEX (default
   ai103-policies-v1), determines vector dimensions from the actual embedding response and
   uploads five synthetic records. Use a NEW index name when changing dimensions/schema.
5. Allow indexing to become queryable, then run live=true, variant=default. Compare keyword,
   vector, hybrid and semantic results. If semantic ranking is unavailable, first test the other
   modes, then enable the feature or record that sub-experiment as blocked.
6. Inspect the index in Search Explorer. Verify the tenant field is filterable and that the
   application query filters by authenticated tenant. Do not allow a model/user to supply this scope.
7. Run lab 11 to connect search to a safe grounded answer. Valid source IDs do not prove that
   each sentence is supported; read the cited passage and evaluate manually.

## Portal ingestion and enrichment for lab 10

Create a Storage account and a private Blob container `ai103-documents`. Upload the synthetic
text files and receipt.png. In Search's **Identity** enable a managed identity; grant it Storage
Blob Data Reader on the source container/account. Give the indexer any additional model/service
permissions required by the chosen enrichment/vectorizer.

Use **Import data** (or the available import/vectorization wizard). Choose Blob Storage,
configure the connection with managed identity where supported, select your container, and
create learning-only data source/indexer/index names. Enable content extraction and OCR for
image content. Select text split, entity/key-phrase enrichment and a supported embedding stage
as available. Inspect the generated skillset JSON: inputs must match earlier outputs; normalized
images feed OCR; merged text/chunks feed downstream enrichment. Use a small one-time run first.

Run the indexer, inspect execution history, failed-item counts and enrichment results. Query
text that appears only in the receipt image. Change a document, rerun, and check the result.
Test a source deletion and configure/verify deletion detection; removing a blob is not always
sufficient to remove its old index entry. Record provenance IDs and ingestion timestamps.

## Custom skill extension

`extensions/custom_skill/` contains a Web API skill contract and a local handler that marks
retail product codes. Run its contract test. For cloud use host it behind an authenticated
HTTPS endpoint, add the custom skill to your skillset, map its input to text and its output
to an index field, then rerun a small batch. Handle the per-record `errors`/`warnings` arrays;
HTTP 200 alone does not imply every record enriched correctly. The example does not deploy a
public endpoint automatically.

Reference: https://learn.microsoft.com/en-us/azure/search/search-get-started-vector
Reference: https://learn.microsoft.com/en-us/azure/search/tutorial-skillset
