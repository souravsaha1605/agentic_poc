"""The reviewed six capabilities, sharing one small validated plan contract."""

from contracts import AnalysisPlan
from tool_executor import ALLOWED_TOOLS

TOOLS = [
    {
        "type": "function",
        "name": name,
        "description": name.replace("_", " "),
        "parameters": AnalysisPlan.model_json_schema(),
    }
    for name in ALLOWED_TOOLS
]
