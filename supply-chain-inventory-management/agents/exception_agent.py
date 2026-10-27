"""
agents/exception_agent.py
=========================
Main agent orchestration loop — the heart of the platform.

PURPOSE
-------
Implements the agentic loop that drives the entire exception-management
workflow (BRD §20, §23):

  User query
      |
      v
  LLM (Azure OpenAI Responses API)  <--- system prompt + tools
      |
      +--> function_call?  -- yes -->  tool_executor.execute()
      |                                   |
      |                                   v
      |                              tool result fed back to LLM
      |                                   |
      +--> function_call?  -- no  -->  return final text response

ARCHITECTURE ROLE
-----------------
  app.py  -->  ExceptionAgent.run(query)
                    |
                    +--> client.responses.create(model, input, tools)
                    +--> loop: extract tool_calls -> execute -> feed back
                    +--> track API call count (MAX_API_CALLS = 10)
                    +--> return final response text

API CALL BUDGET
--------------
Each call to client.responses.create() counts as ONE API call.
The agent enforces a hard limit of MAX_API_CALLS (10) per run.
If the budget is exhausted, the agent returns the best partial response
rather than making additional calls.

BRD COMPLIANCE
--------------
  §20  (Agent Architecture)   – orchestrated multi-agent via single loop
  §21  (Tool Layer)           – tools are defined, typed, and mapped
  §24  (LLM Requirements)     – LLM reasons over tool results, not raw data
  §26  (Guardrails)          – API call limit, tool validation, policy engine
  §28  (Observability)       – each tool call and API call is printed for tracing
"""

import json

from client import client
from config import AZURE_OPENAI_DEPLOYMENT, MAX_API_CALLS
from prompts import EXCEPTION_AGENT_INSTRUCTIONS
from tool_registry import TOOLS
from tool_executor import ToolExecutor
from policy_engine import PolicyEngine


class ExceptionAgent:
    """
    Orchestrates the LLM + tool-calling loop for supply chain exception
    investigation and resolution.

    USAGE:
        agent = ExceptionAgent()
        response = agent.run("Investigate exception EXC-001")
        print(response)
    """

    def __init__(self):
        # Tool executor — validates and routes LLM tool calls
        self.executor = ToolExecutor()

        # Policy engine — deterministic business rules (external to LLM)
        self.policy = PolicyEngine()

        # API call counter — enforces the MAX_API_CALLS budget
        self.api_call_count = 0

    def run(self, user_prompt: str, verbose: bool = True) -> str:
        """
        Execute the agent loop for a single user query.

        Parameters:
            user_prompt : str  – natural language query from the user
            verbose     : bool  – if True, print trace info for observability

        Returns:
            str – the agent's final text response
        """
        # -------------------------------------------------------------------
        # Build the initial conversation with system prompt + user query
        # -------------------------------------------------------------------
        conversation = [
            {
                "role": "system",
                "content": EXCEPTION_AGENT_INSTRUCTIONS
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]

        # -------------------------------------------------------------------
        # Main agentic loop — continues until:
        #   1. The LLM returns no tool calls (final response)
        #   2. The API call budget is exhausted
        # -------------------------------------------------------------------
        while True:
            # --- Check API call budget ---
            if self.api_call_count >= MAX_API_CALLS:
                if verbose:
                    print(f"\n[GUARDRAIL] API call budget exhausted "
                          f"({self.api_call_count}/{MAX_API_CALLS}). "
                          "Returning last available response.")
                # Return a summary of what was gathered so far
                return (
                    "I have reached the maximum number of API calls for this "
                    "session. Based on the evidence gathered so far, please "
                    "review the tool outputs above. If you need further "
                    "investigation, please start a new session."
                )

            # --- Call the LLM ---
            self.api_call_count += 1
            if verbose:
                print(f"\n{'='*60}")
                print(f"API CALL {self.api_call_count}/{MAX_API_CALLS}")
                print(f"{'='*60}")

            response = client.responses.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                input=conversation,
                tools=TOOLS
            )

            # --- Extract any tool calls from the LLM response ---
            tool_calls = [
                item
                for item in response.output
                if item.type == "function_call"
            ]

            # --- If no tool calls, the LLM has produced its final answer ---
            if not tool_calls:
                if verbose:
                    print(f"\n[AGENT] Final response received (no more tool calls)")
                return response.output_text

            # --- Execute each tool call and feed results back ---
            for tool_call in tool_calls:
                if verbose:
                    print(f"\n[TOOL CALL] {tool_call.name}")
                    print(f"  Arguments: {tool_call.arguments}")

                try:
                    arguments = json.loads(tool_call.arguments)
                    tool_result = self.executor.execute(
                        tool_name=tool_call.name,
                        arguments=arguments
                    )

                    if verbose:
                        # Truncate large results for display
                        result_str = json.dumps(tool_result, default=str)
                        if len(result_str) > 500:
                            result_str = result_str[:500] + "..."
                        print(f"  Result: {result_str}")

                except Exception as e:
                    # If a tool fails, report the error to the LLM so it
                    # can adjust its approach (graceful degradation, BRD §31)
                    tool_result = {"error": str(e)}
                    if verbose:
                        print(f"  ERROR: {e}")

                # Append the tool call and its output to the conversation
                conversation.append(tool_call)
                conversation.append({
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": json.dumps(tool_result, default=str)
                })

            # Loop continues — the LLM will see the tool results and either
            # call more tools or produce its final answer.

    def reset(self):
        """Reset the API call counter for a new session."""
        self.api_call_count = 0