# Source basis and version boundaries

Primary supplied reference: SOURCE_HANDBOOK.docx, copied unchanged from your upload.
The course adds original code, synthetic data and experiments. It does not bundle the Udemy
course or claim to have read the handbook's upstream source files. Portal/API references were
checked during creation on 22 October 2026; Azure screens, SDKs and preview contracts may change.

Start with the official AI-103 study guide:
https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-103

Service-specific primary references are linked beside each setup guide. Notable boundaries:

- New Foundry prompt-agent example: azure-ai-projects >=2.3,<3, distinct from classic 1.x.
- General chat/embedding path: OpenAI-compatible Azure v1 API, actual deployment names configured by you.
- Azure Search sample: REST 2024-07-01.
- Content Safety sample: REST 2024-09-01, four-level text severity explicitly selected.
- Content Understanding basic analysis: REST 2025-11-01.
- Image generation/edit: deployment-scoped 2025-04-01-preview, model compatibility required.
- Video: Azure jobs preview interface, access/model compatibility required.
- MCP: intentionally v1 package family in its own dependency set.
- Model-assisted evaluations: Azure AI Evaluation SDK family; compatibility must be tested live.

These are explicit implementation choices, not a claim that each is the latest API for every service.
Retain a dependency lock from a successful environment before promoting a real application.
