"""Adapted from the Foundry Responses API quickstart, PDF page 3066."""
import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential


def main():
    with DefaultAzureCredential() as credential, AIProjectClient(
        endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        credential=credential,
    ) as project, project.get_openai_client() as client:
        answer = client.responses.create(
            model=os.environ["FOUNDRY_MODEL_NAME"],
            instructions="Explain cloud development concepts using concrete examples.",
            input="What is the difference between a model deployment and a project?",
        )
        print(answer.output_text)


if __name__ == "__main__":
    main()
