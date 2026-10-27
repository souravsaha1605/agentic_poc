# Azure setup for lab 29

Follow [docs/setup/10_DOCUMENTS_AND_MEDIA.md](../../docs/setup/10_DOCUMENTS_AND_MEDIA.md) in order, then return to [README.md](README.md).
For Databricks secrets/authentication use [DATABRICKS.md](../../docs/setup/DATABRICKS.md).

Before live execution verify:

- Resource is in the intended learning subscription/group and supported region.
- The endpoint belongs to the intended API family and deployment/analyzer name exists.
- The actual notebook/service identity has the required data permissions.
- Secret scope keys match `databricks/secret_mapping.json` for this lab.
- Network connectivity and private DNS, when applicable, are tested from the actual driver.

Use variant=default initially.

Completion evidence: A printed job ID and outputs/generated.mp4 when the supported service finishes. Preview/access availability can block this lab.

Reference-image experiment: use the included `data/media/video_reference.png` (1280x720). Upload it to your volume and set input_file to that path. It matches the default VIDEO_SIZE.
