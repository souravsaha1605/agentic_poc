# Documents vision speech media and Content Understanding

## Vision and visual safety

Deploy a vision-capable chat model in Foundry and set MODEL_VISION. Configure Content Safety
as in guide 03. Use the included `data/media/product.png` and `receipt.png`: both are generated
synthetic test fixtures, not photographs. Run lab 24 live. Describe visible regions, alt text
and uncertainty; avoid claiming unseen causes. For multiple images, extend the user content
list with another image_url item and explicitly request comparison by image label.

## Document Intelligence

In Azure Portal create a Document Intelligence resource (or supported equivalent capability),
then record DOCUMENT_ENDPOINT and DOCUMENT_KEY. Open Document Intelligence Studio, select a
prebuilt receipt/layout model, upload receipt.png and inspect its fields and page regions.
Run lab 25 using the same image; compare the programmatic result with Studio. Check currency,
line totals and confidence before downstream decisions.

For a custom extraction exercise, prepare several synthetic layouts, use a private Blob
container, label the target fields in Studio, train a model and evaluate on unseen layouts.
Do not train and evaluate on the same copies. Record model ID and change the `model` argument
in media.document to your custom ID for a second run. Custom model training is a portal-guided
extension; no trained custom model is bundled.

## Content Understanding

Use a supported Foundry resource and Content Understanding Studio. Complete its model deployment
and model-mapping prerequisites; simply having a chat deployment may be insufficient. The
course targets GA API 2025-11-01 for basic analysis. Record CU_ENDPOINT, CU_KEY and CU_ANALYZER.
The default is prebuilt-invoice for a wiring experiment; for receipt-specific fields create
the custom analyzer below or use an appropriate available prebuilt analyzer.

1. Open the analyzer creation workflow and choose document input. Upload the synthetic receipt.
2. Define fields ProductCode (string), Total (number), Currency (string) and PurchaseDate (date
   if supported). Add precise descriptions and required evidence/grounding options available
   in the current UI. Test against the image and inspect the raw output.
3. Save as a learning analyzer and copy its analyzer ID to CU_ANALYZER. Run lab 26 live.
   It submits bytes, polls the returned operation location and stops at a deadline.
4. Use markdown/field output as ingestion input, retaining source page/region metadata. Do not
   flatten all structure away before evaluating retrieval quality.
5. Repeat with an image/audio/video analyzer supported by your resource. `prebuilt-imageSearch`,
   `prebuilt-audioSearch` and `prebuilt-videoSearch` are documented families; confirm available
   IDs/capabilities in your environment. Use your own short consented audio/video or generated
   test media. Compare transcript-only output with time-aligned visual/audio evidence.
6. The historical pro-mode API is retired. Use the current agentic document extension and the migration guide in azure_execution/content_understanding; keep ordinary GA analysis for other modalities.

## Image generation and editing

Deploy a supported GPT-image-family model with generation/edit capability and required access.
Set MODEL_IMAGE and IMAGE_API_VERSION. The sample uses the documented deployment-scoped
2025-04-01-preview image API; confirm that your deployed model supports it before calling.
Run lab 28 with live=true. For variant=edit it uses product.png plus mask.png: transparent
regions are editable, opaque product regions are protected by the editing request. Input and
mask dimensions must match. Inspect the result; masking is guidance, not a guarantee.

Change one supported control at a time. Save prompt/model/settings with the output and apply
visual moderation and brand review. Add a visible synthetic-content label/watermark for assets
used outside the exercise, and preserve provider provenance metadata where supported.

## Video generation and editing

Provision an available supported video model only when you reach lab 29. Access, region and
preview features vary. Set MODEL_VIDEO; optional VIDEO_SIZE and VIDEO_SECONDS go in config_json. The reviewed adapter targets the
Sora 2 v1 Videos API, with text/image input and remix of a completed video ID.
Verify this interface matches the deployment's current code example. If it exposes a different
API, keep this lab blocked until you adapt to that documented contract; never guess a version.

Run text-only first. Record the video ID, then try a correctly sized reference image with input_file; use variant=remix with VIDEO_ID for generated-video edits.
Supported controls include those accepted by YOUR model; the sample uses a 4-second 1280x720 job.
Inspect temporal consistency, unwanted changes, unsafe visual content, embedded text and brand
constraints. A timeout leaves a potentially running billed job; inspect it before resubmitting.

References:
- https://learn.microsoft.com/en-us/python/api/overview/azure/ai-documentintelligence-readme?view=azure-python
- https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/quickstart/use-rest-api
- https://learn.microsoft.com/en-us/rest/api/contentunderstanding/content-analyzers/analyze-binary?view=rest-contentunderstanding-2025-11-01
- https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/dall-e
- https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/video-generation
