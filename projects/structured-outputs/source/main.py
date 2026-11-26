"""Exercise the Responses JSON Schema pattern from Microsoft Learn."""
import argparse
import json
import os

EVENT_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "date": {"type": "string"},
        "participants": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["name", "date", "participants"],
    "additionalProperties": False,
}
EXAMPLE = '{"name":"Science fair","date":"Friday","participants":["Alice","Bob"]}'


def request_event():
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential

    with DefaultAzureCredential() as credential, AIProjectClient(
        endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"], credential=credential
    ) as project, project.get_openai_client() as client:
        response = client.responses.create(
            model=os.environ["FOUNDRY_MODEL_NAME"],
            input="Extract the event: Alice and Bob are going to a science fair on Friday.",
            text={
                "format": {
                    "type": "json_schema",
                    "name": "calendar_event",
                    "schema": EVENT_SCHEMA,
                    "strict": True,
                }
            },
        )
        if response.status != "completed" or not response.output_text:
            raise RuntimeError(f"No completed structured response: {response.status}")
        return response.output_text


def main():
    from jsonschema import validate

    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    event = json.loads(request_event() if args.live else EXAMPLE)
    validate(instance=event, schema=EVENT_SCHEMA)
    print("Live model extraction" if args.live else "Offline fixture validated against the event schema")
    print(json.dumps(event, indent=2))


if __name__ == "__main__":
    main()
