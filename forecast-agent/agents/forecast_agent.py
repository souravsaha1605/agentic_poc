import json

from client import client
from config import AZURE_OPENAI_DEPLOYMENT
from prompts import SUPPLY_CHAIN_AGENT_INSTRUCTIONS
from tool_registry import TOOLS
from tool_executor import ToolExecutor


class ForecastAgent:

    def __init__(self):

        self.executor = ToolExecutor()
        

    def run(self, user_prompt: str):

        conversation = [

            {
                "role": "system",
                "content": SUPPLY_CHAIN_AGENT_INSTRUCTIONS
            },

            {
                "role": "user",
                "content": user_prompt
            }

        ]

        while True:

            response = client.responses.create(

                model=AZURE_OPENAI_DEPLOYMENT,

                input=conversation,

                tools=TOOLS

            )

            print("\n==============================")
            print("LLM Response")
            print("==============================")
            print(response.output)

            tool_calls = [

                item

                for item in response.output

                if item.type == "function_call"

            ]

            if not tool_calls:

                return response.output_text

            for tool_call in tool_calls:

                arguments = json.loads(
                    tool_call.arguments
                )

                tool_result = self.executor.execute(

                    tool_name=tool_call.name,

                    arguments=arguments

                )

                conversation.append(tool_call)

                conversation.append(

                    {
                        "type": "function_call_output",

                        "call_id": tool_call.call_id,

                        "output": json.dumps(
                            tool_result,
                            default=str
                        )

                    }

                )