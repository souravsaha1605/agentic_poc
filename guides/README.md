# Microsoft Foundry study and practice guide

Start with the [official Microsoft Learn topic index](source-index.md). It follows the published navigation and maps articles to the five PDFs and to local practice projects. [Word index](source-index.docx)

1. Study the [terminology guide](foundry-terminology.md). Read the **Very important** entries first, then look up the concepts used by the project you choose. [Word terminology guide](foundry-terminology.docx)
2. Choose a scenario in the [project catalog](../projects/README.md). The two offline exercises cover embedding-based ranking and structured outputs. Continue with a prompt agent, a hosted agent, an agent with File Search, or a toolbox.
3. Consult the [troubleshooting guide](foundry-troubleshooting.md) for diagnostic checks, remedies, and recovery tests. [Word troubleshooting guide](foundry-troubleshooting.docx)
4. Use the [walkthrough inventory](../projects/source-walkthroughs.md) to explore additional tutorials, sample repositories, and project ideas.

## Regenerate the Word documents

From the repository root with Pandoc installed:

```bash
for guide in source-index foundry-terminology foundry-troubleshooting; do
  pandoc --from=markdown+gfm_auto_identifiers --standalone --toc "guides/$guide.md" -o "guides/$guide.docx"
done
```
