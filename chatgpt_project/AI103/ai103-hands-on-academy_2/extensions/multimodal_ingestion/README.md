# multimodal ingestion

Start with [RUNBOOK.md](RUNBOOK.md).

Complete lab 26. Copy the full volume path to a real 26_content_understanding.json into input_file.
Run offline to transform it; inspect source/segment/time/page metadata. For live indexing set
config_json={"SEARCH_INDEX":"ai103-media-v1"}, create the lab 09 embedding/search secrets, and run.
This is a separate index from policies. Query it using lab 09 with the same SEARCH_INDEX override.
Expected: nonempty chunks and indexed count. Use a new index when changing embedding dimensions.
If your analyzer returns fields without markdown/text, choose an analyzer that produces them first;
this script does not manufacture passages from unsupported schema.
