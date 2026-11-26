"""Adapted from the Foundry prompt agent quickstart, PDF page 3056."""
import os

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity import DefaultAzureCredential


def main():
    name = os.environ["FOUNDRY_AGENT_NAME"]
    with DefaultAzureCredential() as credential, AIProjectClient(
        endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        credential=credential,
    ) as project:
        version = project.agents.create_version(
            agent_name=name,
            definition=PromptAgentDefinition(
                model=os.environ["FOUNDRY_MODEL_NAME"],
                instructions="You are a helpful assistant that answers general questions.",
            ),
        )
        print(f"Agent {version.name}, version {version.version}")
        with project.get_openai_client(agent_name=name) as client:
            conversation = client.conversations.create()
            for question in (
                "What is the size of France in square miles?",
                "And what is the capital city?",
            ):
                answer = client.responses.create(
                    conversation=conversation.id, input=question
                )
                print(answer.output_text)


if __name__ == "__main__":
    main()
