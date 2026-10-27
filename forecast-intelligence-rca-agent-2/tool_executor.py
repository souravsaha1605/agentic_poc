"""
tool_executor.py -- Strict dispatch layer with allowlist, Pydantic
validation, max-call guard, and standardised errors.
============================================================================

PURPOSE
-------
Sits between the LLM and the service-layer tools.  When the LLM requests
a tool call, the agent passes the tool name and arguments here.  The
ToolExecutor performs four safety checks before dispatching:

  1. ALLOWLIST CHECK (BRD SS29): Is the requested tool in the approved set?
  2. MAX-CALL GUARD (BRD SS30): Have we exceeded the per-message limit?
  3. PYDANTIC VALIDATION (BRD SS28): Do the arguments match the expected schema?
  4. ERROR HANDLING (BRD SS28): Wrap any exception in a standardised ToolResult.

If any check fails, a ToolResult with success=False and a descriptive error
is returned to the LLM so it can adjust its behaviour.

DESIGN RATIONALE
----------------
- The allowlist is a hard boundary: even if the LLM hallucinates a tool
  name, the executor will reject it.
- Pydantic validation prevents malformed arguments from reaching services.
- The max-call guard prevents infinite tool-call loops.

BRD REFERENCES: SS28 (Error Handling), SS29 (Trust Boundary), SS30 (Loop Protection).
"""

import json
import logging
import time
from typing import Any, Dict, Tuple

from models import (
    RCARequest,
    ScenarioComparisonRequest,
    AnalyticalQueryRequest,
    ToolResult,
)
from tools.forecast_rca_tools import (
    run_analytical_query,
    run_forecast_rca,
    compare_scenarios,
)

logger = logging.getLogger(__name__)


class ToolExecutor:
    """
    Validates, dispatches, and guards all LLM-requested tool calls.

    Usage:
        executor = ToolExecutor(max_tool_calls=6)
        executor.reset_call_count()         # call at the start of each user message
        result = executor.execute("get_forecast_context", {"product_id": "SKU-001"})
    """

    # Strict allowlist (BRD SS29)
    # Maps tool name -> (function, Pydantic request model)
    # Only tools listed here can ever be called by the LLM.
    _ALLOWED: Dict[str, Tuple[Any, Any]] = {
        "run_analytical_query":      (run_analytical_query,  AnalyticalQueryRequest),
        "run_forecast_rca":           (run_forecast_rca,     RCARequest),
        "compare_scenarios":          (compare_scenarios,    ScenarioComparisonRequest),
    }

    def __init__(self, max_tool_calls: int = 6):
        self.max_tool_calls = max_tool_calls
        self._call_count = 0

    # ------------------------------------------------------------------
    def reset_call_count(self):
        """Reset the per-message tool-call counter."""
        self._call_count = 0

    # ------------------------------------------------------------------
    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single tool call with full validation.
        Returns a dict suitable for JSON serialisation to the LLM.
        """
        start = time.time()

        # 1. Allowlist check (BRD §29)
        if tool_name not in self._ALLOWED:
            logger.warning("Rejected unknown tool: %s", tool_name)
            return ToolResult(
                success=False, tool_name=tool_name,
                error=f"Unknown tool '{tool_name}'. Only approved tools may be called.",
            ).model_dump()

        # 2. Max-call guard (BRD §30)
        if self._call_count >= self.max_tool_calls:
            logger.warning("Max tool calls reached (%d)", self.max_tool_calls)
            return ToolResult(
                success=False, tool_name=tool_name,
                error=f"Maximum tool calls ({self.max_tool_calls}) reached for this message.",
            ).model_dump()

        self._call_count += 1
        func, request_model = self._ALLOWED[tool_name]

        # 3. Pydantic validation (BRD §28)
        try:
            request = request_model(**arguments)
        except Exception as exc:
            logger.warning("Validation failed for %s: %s", tool_name, exc)
            return ToolResult(
                success=False, tool_name=tool_name,
                error=f"Invalid arguments for '{tool_name}': {exc}",
            ).model_dump()

        # 4. Execute with error handling (BRD §28)
        try:
            result = func(request)
            elapsed = (time.time() - start) * 1000

            # Wrap in ToolResult if not already
            if isinstance(result, ToolResult):
                result.execution_time_ms = elapsed
                return result.model_dump()

            if isinstance(result, dict) and result.get("success") is False:
                return result

            return ToolResult(
                success=True,
                tool_name=tool_name,
                data=result,
                execution_time_ms=elapsed,
            ).model_dump()

        except Exception as exc:
            logger.exception("Tool execution failed: %s", tool_name)
            return ToolResult(
                success=False, tool_name=tool_name,
                error=f"Tool execution error: {exc}",
            ).model_dump()