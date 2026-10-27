# Read the shared code

Start with a lesson run.py, then follow its imports.

| Symbol | Responsibility |
|---|---|
| `api.py:application` | Read the implementation and its calling lesson. |
| `cloud.py:request` | Make a bounded HTTPS call; only explicitly safe operations receive status retries. |
| `cloud.py:cognitive_headers` | Read the implementation and its calling lesson. |
| `cloud.py:model_client` | Build the Azure v1 client using a service key or Entra token provider. |
| `cloud.py:chat` | Call a configured chat deployment; reject filtered, truncated or refused output. |
| `cloud.py:embed` | Request one embedding per input and preserve input order. |
| `cloud.py:safety` | Apply the teaching block threshold to Azure Content Safety category scores. |
| `cloud.py:shield` | Inspect direct user and indirect document prompt attacks. |
| `cloud.py:translate` | Translate one string with the configured Translator resource. |
| `cloud.py:poll_operation` | Poll only the original service host so credentials cannot be redirected. |
| `common.py:load_env` | Load optional terminal configuration; Databricks explicitly disables .env. |
| `common.py:env` | Read one required setting and stop with setup guidance when it is missing. |
| `common.py:args` | Parse the same options used by terminal commands and Databricks widgets. |
| `common.py:save` | Persist and print a result within the configured output directory. |
| `common.py:read` | Read bundled synthetic JSON relative to the project root. |
| `common.py:fixture` | Label fixed demonstration data so it cannot be mistaken for a service response. |
| `common.py:run_async` | Works in a terminal and inside Databricks' already-running event loop. |
| `domain.py:Principal` | Read the implementation and its calling lesson. |
| `domain.py:tokens` | Read the implementation and its calling lesson. |
| `domain.py:retrieve` | Retrieve only documents belonging to the trusted principal tenant. |
| `domain.py:redact` | Mask email addresses for a small local demo; not a complete PII system. |
| `domain.py:local_guard` | Reject empty/oversized input and flag a deliberately small attack baseline. |
| `domain.py:validate_answer` | Validate output shape and known source IDs, not factual entailment. |
| `domain.py:order_for` | Enforce both owner and tenant before returning an order. |
| `domain.py:eligibility` | Compute business eligibility from trusted records, not model judgment. |
| `domain.py:allowed_tools` | Derive tool permissions from trusted role state. |
| `domain.py:execute_tool` | Validate permission and arguments before invoking an allowlisted tool. |
| `domain.py:Ledger` | SQLite local teaching ledger: approval + deduplication + atomic simulated effects. |
| `domain.py:TTLCache` | Read the implementation and its calling lesson. |
| `domain.py:cosine` | Compare vector direction; reject incompatible embedding dimensions. |
| `domain.py:chunk` | Split text with word overlap; this teaching splitter is not a tokenizer. |
| `enrichment.py:enrich` | Read the implementation and its calling lesson. |
| `enterprise.py:sales` | Read the implementation and its calling lesson. |
| `flows.py:rag` | Compose input screening, scoped retrieval, grounding, citation validation and output screening. |
| `flows.py:agent` | Run a bounded tool loop; backend code retains authorization regardless of model requests. |
| `language.py:preprocess` | Detect language, redact PII, then extract limited support-message signals. |
| `media.py:vision` | Request a visual description from image bytes without granting tools. |
| `media.py:document` | Analyze binary input using a Document Intelligence model. |
| `media.py:understand` | Submit binary media to a configured Content Understanding analyzer. |
| `media.py:image_job` | Generate or mask-edit one image, then save the returned PNG. |
| `memory.py:Memory` | Read the implementation and its calling lesson. |
| `memory.py:window` | Keep the newest messages within a character budget; real token budgets need a tokenizer. |
| `notebook.py:configuration` | Parse settings without allowing credentials to be placed in visible widgets. |
| `notebook.py:required_secrets` | Select the minimum credentials for the actual branch being executed. |
| `notebook.py:validate_variant` | Read the implementation and its calling lesson. |
| `notebook.py:output_directory` | Require a learner-owned UC volume; tests substitute this boundary, not a real mount. |
| `notebook.py:run` | Execute one lesson with clean configuration and a unique evidence directory. |
| `search.py:call` | Read the implementation and its calling lesson. |
| `search.py:index_name` | Read the implementation and its calling lesson. |
| `search.py:ingest` | Index the supplied five-document synthetic corpus. |
| `search.py:ingest_rows` | Embed records and upload them to an explicitly named learning index. |
| `search.py:search` | Apply trusted tenant scope and the selected lexical/vector/reranking method. |
| `speech.py:transcribe` | Read the implementation and its calling lesson. |
| `speech.py:synthesize` | Read the implementation and its calling lesson. |
| `video.py:render` | Return a saved MP4 or an actionable failure; never silently resubmit. |
