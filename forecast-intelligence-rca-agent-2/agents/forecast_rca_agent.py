"""
agents/forecast_rca_agent.py
============================================================================

PURPOSE
-------
Session-aware agent orchestration for the Forecast Intelligence & RCA Agent.
This is the central orchestrator that ties together all components:

  config.py -> client.py -> models.py -> prompts.py -> tool_registry.py
  -> tool_executor.py -> services/forecast_rca_service.py -> this module

PIPELINE (per user message)
--------------------------
  1. Save user turn to conversation_turns (Delta)
  2. Entity resolution -- extract and resolve product/region from prompt
  3. Determine scenario action -- CONTINUE, NEW, UPDATE, or AMBIGUOUS
  4. Handle ambiguity -- ask clarification if multiple candidates
  5. Create or update scenario state (SCD-Type-2 in Delta)
  6. Build conversation with system prompt + scenario context + history
  7. Agent loop -- bounded LLM calls with tool execution (BRD SS30)
     - LLM decides which tools to call
     - ToolExecutor validates and dispatches each call
     - Tool results fed back to LLM for next turn
     - Loop exits when LLM produces a text response or max turns reached
  8. Update scenario state with tool results
  9. Save assistant turn to conversation_turns (Delta)
 10. Update in-memory conversation cache

KEY UPGRADES OVER ORIGINAL forecast-agent (BRD SS40)
---------------------------------------------------
  - Persistent session state (scenario + conversation memory in Delta)
  - Entity resolution before tool selection (BRD SS43)
  - Message intent classification + scenario action (BRD SS15)
  - Bounded tool loop (MAX_TOOL_CALLS_PER_MESSAGE)
  - Structured tool errors
  - Response grounding (entity, period, as-of)
  - Scenario version handling (SCD-Type-2)

BRD REFERENCES: SS15 (Intent/Action), SS16 (Scenario Lifecycle),
               SS30 (Loop Protection), SS40 (Code Changes), SS43 (Key Design Decision).
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from client import client
from config import (
    AZURE_OPENAI_DEPLOYMENT,
    MAX_AGENT_TURNS,
    MAX_TOOL_CALLS_PER_MESSAGE,
    MAX_HISTORY_TOKENS,
    SCENARIO_NEW, SCENARIO_ACTIVE, SCENARIO_ANALYZING,
    SCENARIO_RCA_IDENT, SCENARIO_WHAT_IF, SCENARIO_OUTCOME,
    INTENT_RCA, INTENT_WHAT_IF, INTENT_OUTCOME_UPDATE,
    ACTION_CONTINUE, ACTION_NEW, ACTION_UPDATE, ACTION_AMBIGUOUS,
)
from models import (
    EntityContext, TimeRange, ConversationTurn,
    MessageClassification, ScenarioState, AgentResponse,
)
from prompts import SYSTEM_PROMPT
from tool_registry import TOOLS
from tool_executor import ToolExecutor
from services.forecast_rca_service import (
    entity_service, conversation_service, scenario_service,
)

logger = logging.getLogger(__name__)


class ForecastIntelligenceAgent:
    """
    Session-aware conversational agent with persistent scenario memory.

    Each instance is bound to a session_id.  On init, it loads any existing
    conversation history and active scenario from Delta.  Subsequent calls
    to run() continue that session, maintaining context across turns.

    Args:
        session_id: Optional session identifier.  If None, a new one is generated.
    """

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"SES-{uuid.uuid4().hex[:8].upper()}"
        self.executor = ToolExecutor(max_tool_calls=MAX_TOOL_CALLS_PER_MESSAGE)
        self.active_scenario: Optional[ScenarioState] = None
        self._conversation: List[Dict[str, str]] = []
        self._load_or_init_session()

    # ------------------------------------------------------------------
    def _load_or_init_session(self):
        """Load existing conversation history and active scenario from Delta."""
        try:
            history = conversation_service.get_history(self.session_id)
            self._conversation = [
                {"role": h["role"], "content": h["message"]}
                for h in history
            ]
        except Exception:
            self._conversation = []

        try:
            self.active_scenario = scenario_service.load_active_scenario(self.session_id)
        except Exception:
            self.active_scenario = None

    # ------------------------------------------------------------------
    def run(self, user_prompt: str) -> AgentResponse:
        """Process a user message through the full agent pipeline."""
        turn_id = conversation_service.get_next_turn_id(self.session_id)
        tools_called: List[str] = []

        # 1. Save user turn
        conversation_service.save_turn(ConversationTurn(
            session_id=self.session_id,
            turn_id=turn_id,
            role="user",
            message=user_prompt,
        ))

        # 2. Entity resolution (mandatory, BRD §6.4)
        entities = self._extract_entities(user_prompt)
        resolved = entity_service.resolve_entity(
            product_id=entities.get("product_id"),
            region=entities.get("region"),
            store_id=entities.get("store_id"),
            category=entities.get("category"),
        )

        # 3. Determine scenario action (simplified deterministic logic)
        scenario_action = self._determine_scenario_action(user_prompt, resolved)

        # 4. Handle ambiguity
        if resolved.ambiguous:
            clarification = (
                f"Multiple products match '{resolved.product_name}'. "
                f"Please specify: {', '.join([c.get('product_id','') for c in resolved.candidates])}"
            )
            self._save_assistant_turn(turn_id, clarification, tools_called)
            return AgentResponse(response=clarification, scenario_action=ACTION_AMBIGUOUS)

        # 5. Create/update scenario
        if scenario_action == ACTION_NEW:
            self.active_scenario = scenario_service.create_scenario(
                session_id=self.session_id,
                entities=resolved,
                analysis_type=self._classify_intent(user_prompt),
            )
        elif scenario_action == ACTION_CONTINUE and self.active_scenario:
            # Merge resolved entities with existing scenario state
            if not resolved.product_id and self.active_scenario.resolved_entities.product_id:
                resolved = self.active_scenario.resolved_entities
        elif not self.active_scenario:
            self.active_scenario = scenario_service.create_scenario(
                session_id=self.session_id,
                entities=resolved,
                analysis_type=self._classify_intent(user_prompt),
            )

        # 6. Build conversation with scenario context
        scenario_context = self._build_scenario_context(resolved)
        conversation = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": scenario_context},
        ]
        # Trim history to token budget
        for msg in self._conversation[-10:]:
            conversation.append(msg)
        conversation.append({"role": "user", "content": user_prompt})

        # 7. Agent loop (bounded, BRD §30)
        self.executor.reset_call_count()
        agent_turn = 0
        response_text = ""

        while agent_turn < MAX_AGENT_TURNS:
            agent_turn += 1

            try:
                response = client.responses.create(
                    model=AZURE_OPENAI_DEPLOYMENT,
                    input=conversation,
                    tools=TOOLS,
                )
            except Exception as exc:
                logger.error("LLM call failed: %s", exc)
                response_text = (
                    f"I encountered an error connecting to the AI service. "
                    f"Please check the .env credentials and try again. Error: {exc}"
                )
                break

            tool_calls = [
                item for item in response.output
                if item.type == "function_call"
            ]

            if not tool_calls:
                response_text = response.output_text
                break

            for tool_call in tool_calls:
                tool_name = tool_call.name
                tools_called.append(tool_name)

                try:
                    arguments = json.loads(tool_call.arguments)
                except json.JSONDecodeError:
                    arguments = {}

                # Inject resolved entities if missing
                if resolved.product_id and "product_id" in arguments and not arguments.get("product_id"):
                    arguments["product_id"] = resolved.product_id
                if resolved.region and "region" in arguments and not arguments.get("region"):
                    arguments["region"] = resolved.region

                tool_result = self.executor.execute(tool_name, arguments)

                conversation.append(tool_call)
                conversation.append({
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": json.dumps(tool_result, default=str),
                })

        if not response_text:
            response_text = "I was unable to complete the analysis within the allowed iterations."

        # 8. Update scenario state
        if self.active_scenario:
            self.active_scenario.status = SCENARIO_ACTIVE
            self.active_scenario.last_tool_results = {"tools": tools_called}
            self.active_scenario.updated_at = datetime.now()
            scenario_service.update_scenario(self.active_scenario)

        # 9. Save assistant turn
        intent = self._classify_intent(user_prompt)
        self._save_assistant_turn(turn_id, response_text, tools_called, intent, scenario_action)

        # 10. Update in-memory conversation
        self._conversation.append({"role": "user", "content": user_prompt})
        self._conversation.append({"role": "assistant", "content": response_text})

        return AgentResponse(
            response=response_text,
            scenario_id=self.active_scenario.scenario_id if self.active_scenario else None,
            intent=intent,
            scenario_action=scenario_action,
            tools_called=tools_called,
        )

    # ------------------------------------------------------------------
    def _extract_entities(self, prompt: str) -> Dict[str, str]:
        """Simple deterministic entity extraction from the prompt."""
        prompt_upper = prompt.upper()
        entities: Dict[str, str] = {}

        # Product ID patterns: SKU-001, P0001, SKU0001
        import re
        sku_match = re.search(r'(SKU-\d+|P\d{4}|SKU\d+)', prompt_upper)
        if sku_match:
            entities["product_id"] = sku_match.group(1)

        # Region patterns
        regions = ["NORTH", "SOUTH", "EAST", "WEST", "CENTRAL"]
        for r in regions:
            if r in prompt_upper:
                entities["region"] = r.capitalize()
                break

        # Category patterns
        categories = ["BEVERAGES", "DAIRY", "HOME CARE", "PERSONAL CARE", "SNACKS"]
        for c in categories:
            if c in prompt_upper:
                entities["category"] = c.title()
                break

        return entities

    # ------------------------------------------------------------------
    def _determine_scenario_action(
        self, prompt: str, entities: EntityContext,
    ) -> str:
        """Determine whether to continue, create new, or update the scenario."""
        prompt_upper = prompt.upper()

        # New scenario signals
        new_signals = ["NOW ANALYZE", "START", "NEW", "FORGET", "ANOTHER PRODUCT"]
        if any(s in prompt_upper for s in new_signals):
            # Check if entity actually changed
            if entities.product_id and self.active_scenario:
                if entities.product_id != self.active_scenario.resolved_entities.product_id:
                    return ACTION_NEW
            elif not self.active_scenario:
                return ACTION_NEW
            elif any(s in prompt_upper for s in ["FORGET", "START"]):
                return ACTION_NEW

        # What-if signals
        if "WHAT IF" in prompt_upper:
            return ACTION_UPDATE

        # Outcome update signals
        outcome_signals = ["WE CHANGED", "WE INCREASED", "WE DECREASED", "IMPROVED", "OUTCOME"]
        if any(s in prompt_upper for s in outcome_signals):
            return ACTION_UPDATE

        # Default: continue if scenario exists
        if self.active_scenario:
            return ACTION_CONTINUE

        return ACTION_NEW

    # ------------------------------------------------------------------
    def _classify_intent(self, prompt: str) -> str:
        """Classify message intent (BRD §15A)."""
        prompt_upper = prompt.upper()

        if "WHAT IF" in prompt_upper:
            return INTENT_WHAT_IF
        if any(s in prompt_upper for s in ["WE CHANGED", "IMPROVED", "OUTCOME"]):
            return INTENT_OUTCOME_UPDATE
        if any(s in prompt_upper for s in ["WHY", "ROOT CAUSE", "RCA"]):
            return INTENT_RCA
        if "REVENUE" in prompt_upper:
            return "REVENUE_RETRIEVAL"
        if "INVENTORY" in prompt_upper:
            return "INVENTORY_RETRIEVAL"
        if any(s in prompt_upper for s in ["TREND", "PATTERN", "HISTORICAL"]):
            return "TREND_ANALYSIS"
        if "COMPARE" in prompt_upper:
            return "COMPARISON"
        if "FORECAST" in prompt_upper:
            return "FORECAST_RETRIEVAL"
        return "EXPLANATION"

    # ------------------------------------------------------------------
    def _build_scenario_context(self, entities: EntityContext) -> str:
        """Build scenario context string for the LLM."""
        parts = []
        if self.active_scenario:
            parts.append(f"Active scenario: {self.active_scenario.scenario_id}")
            parts.append(f"Status: {self.active_scenario.status}")
        if entities.product_id:
            parts.append(f"Resolved product: {entities.product_id}")
        if entities.region:
            parts.append(f"Resolved region: {entities.region}")
        if entities.category:
            parts.append(f"Resolved category: {entities.category}")

        context = "\n".join(parts) if parts else "No active scenario context."
        return f"SCENARIO CONTEXT (use these resolved entities, do not ask the user to repeat):\n{context}"

    # ------------------------------------------------------------------
    def _save_assistant_turn(
        self, turn_id: int, message: str,
        tools_called: List[str],
        intent: str = "", scenario_action: str = "",
    ) -> None:
        """Persist the assistant response."""
        try:
            conversation_service.save_turn(ConversationTurn(
                session_id=self.session_id,
                turn_id=turn_id + 1,
                role="assistant",
                message=message,
                scenario_id=self.active_scenario.scenario_id if self.active_scenario else None,
                intent=intent,
                scenario_action=scenario_action,
            ))
        except Exception as exc:
            logger.warning("Could not save assistant turn: %s", exc)