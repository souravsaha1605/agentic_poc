"""Typed result returned by the agent facade.

Input, authorization and analytical plan models live in contracts.py. Keeping
one authoritative schema avoids slightly different tool validation rules.
"""

from typing import Any
from pydantic import BaseModel, Field


class AgentResponse(BaseModel):
    response: str
    scenario_id: str | None = None
    intent: str | None = None
    scenario_action: str | None = None
    tools_called: list[str] = Field(default_factory=list)
    entity: dict[str, Any] | None = None
    evidence: dict[str, Any] | None = None
    scenario_version: int | None = None
    session_version: int | None = None
    success: bool = True
    error_code: str | None = None
