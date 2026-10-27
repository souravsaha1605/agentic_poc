# Search service execution: indexer, OCR and custom enrichment

## Built-in pipeline

1. Complete [Search setup](../../docs/setup/05_SEARCH_AND_INGESTION.md) for a dedicated search
   service, private Blob container and indexer identity. The notebook is a client, not the indexer host.
2. Upload `data/documents/returns-v1.txt` and `data/media/receipt.png` to the source container.
   Keep partner/private data out of this beginner portal index: tenant metadata is not automatically
   inferred from a blob filename. The programmatic lab 09 index has its own explicit tenant field.
3. In Search use **Import data** for a Blob source. Select **Add AI enrichment**, connect the
   required AI service, and enable OCR and text enrichment. A wizard named **Import and vectorize**
   is a different route; use it when you also have an embedding deployment.
4. Choose index name `ai103-enrichment-v1`, a key field, content searchable/retrievable, and
   one-time indexer schedule. Inspect **Skillsets**: OCR input must be normalized images; merging
   must include OCR output before split/embedding. Save the generated definitions for your evidence.
5. Run the indexer. Open **Indexers → Execution history**; require zero failed documents for these
   two inputs. Query `1500` in **Search Explorer**. Inspect the receipt record and extracted text.
6. Modify a policy, rerun, and check the new text. Then configure a supported deletion-detection
   policy on the data source, delete the test blob, rerun and verify removal. A blob deletion alone
   is not proof of index deletion; see the linked service docs if your tier/source lacks the option.

## Deploy and connect the custom skill

1. Run `databricks/extensions/10_custom_enrichment.py` offline. The output contract is
   `values → recordId/data/errors/warnings`; malformed records must report per-record errors.
2. Deploy the API using [App Service](../app_service/README.md). Test `/skill` with a synthetic
   request before wiring it into Search. No model is needed for this regular-expression skill.
3. Open the learning skillset JSON in Azure Portal. Add the object from
   `extensions/custom_skill/skill.template.json`, replacing its URI with your HTTPS `/skill` URL.
   Add `httpHeaders: {"Authorization":"Bearer YOUR_DEMO_TOKEN"}` using the temporary learning
   token. Keep skillset administration tightly scoped: this value is readable by its administrators.
4. Map `inputs[].source` to a real text node in your existing enrichment tree. For the basic
   document-content path use `/document/content`; if your wizard uses merged text, select that
   node instead. Set output targetName `productCodes`. Add an index field `productCodes` of type
   Collection(Edm.String), searchable/retrievable, and an indexer outputFieldMapping from
   `/document/productCodes` to `productCodes`.
5. Reset/rerun only this learning indexer and inspect a K100 record. Expect productCodes=[K100].
   Deliberately use a wrong token once; expect an authentication/indexer error, not silently empty data.
6. Delete the learning endpoint/skillset or rotate the temporary token after the experiment.

This is a complete small hosting exercise, not an enterprise authentication design. Before
production, use the supported managed-identity custom-skill authentication path, validate the
calling identity, narrow app authorization, and remove static tokens from skill definitions.

References:
- https://learn.microsoft.com/en-us/azure/search/tutorial-skillset
- https://learn.microsoft.com/en-us/azure/search/cognitive-search-custom-skill-web-api
