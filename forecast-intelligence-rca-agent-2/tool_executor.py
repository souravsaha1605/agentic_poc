"""Six-tool allowlist with typed plans, a per-turn cap and trusted entitlements."""

from contracts import AnalysisPlan
from tools.forecast_rca_tools import dispatch

ALLOWED_TOOLS = (
    "get_forecast_context",
    "get_inventory_context",
    "get_revenue_context",
    "analyze_historical_pattern",
    "run_forecast_rca",
    "compare_scenarios",
)


class ToolExecutor:
    def __init__(self, business, principal, max_tool_calls=6):
        self.business, self.principal = business, principal
        self.max_tool_calls = min(6, max_tool_calls)
        self._call_count = 0

    def execute(self, tool_name, arguments):
        if tool_name not in ALLOWED_TOOLS:
            raise ValueError("Unknown tool. Arbitrary SQL/code is never accepted.")
        if self._call_count >= self.max_tool_calls:
            raise ValueError("Per-message tool limit reached.")
        self._call_count += 1
        data = dict(arguments)
        data["tool"] = tool_name
        plan = AnalysisPlan.model_validate(data)
        return dispatch(self.business, self.principal, plan)

    def reset_call_count(self):
        self._call_count = 0
