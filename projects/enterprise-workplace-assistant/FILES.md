# File guide

| File | What it does and why it matters |
| --- | --- |
| README.md | Describes the scenario, services, attribution, and expected result. |
| SOURCE-STEPS.md | Records the original walkthrough sequence for reference. |
| RUN-MANUALLY.md | Explains how to reproduce the sample and inspect its output. |
| run.sh | Checks settings, then launches the sample and returns its result. |
| [source/LICENSE](source/LICENSE) | Preserves the license and copyright of the copied upstream code. |
| [source/evaluate.py](source/evaluate.py) | Submits batch evaluation and reports results. |
| [source/evaluation_results.json](source/evaluation_results.json) | Records upstream example results from a prior evaluation. |
| [source/main.py](source/main.py) | Answer employee questions using company policies and external technical guidance. Run batch evaluation against example questions. |
| [source/questions.jsonl](source/questions.jsonl) | Supplies example evaluation questions. |
| [source/requirements.txt](source/requirements.txt) | Pins the verified Azure AI Projects SDK and lists Azure Identity and dotenv for both scripts. |
| [source/sharepoint-sample-data/collaboration-standards.docx](source/sharepoint-sample-data/collaboration-standards.docx) | Provides a sample collaboration standards document to upload to the SharePoint knowledge source. |
| [source/sharepoint-sample-data/data-governance-policy.docx](source/sharepoint-sample-data/data-governance-policy.docx) | Provides a sample data governance policy document to upload to the SharePoint knowledge source. |
| [source/sharepoint-sample-data/remote-work-policy.docx](source/sharepoint-sample-data/remote-work-policy.docx) | Provides a sample remote work policy document to upload to the SharePoint knowledge source. |
| [source/sharepoint-sample-data/security-guidelines.docx](source/sharepoint-sample-data/security-guidelines.docx) | Provides a sample security guidelines document to upload to the SharePoint knowledge source. |
