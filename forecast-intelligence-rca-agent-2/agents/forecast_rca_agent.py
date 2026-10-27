"""Thin, channel-independent facade over the shared conversation service.

Pass the authenticated principal explicitly. Reuse session_id after a restart,
request_id on redelivery, and case_id when resuming a particular owned case.
"""

import uuid
from models import AgentResponse


class ForecastIntelligenceAgent:
    def __init__(self, core, principal, session_id=None):
        self.core = core
        self.principal = principal
        self.session_id = session_id or "SES-" + uuid.uuid4().hex

    def run(self, user_prompt, request_id=None, expected_version=None, case_id=None):
        answer = self.core.handle(
            self.principal,
            {
                "session_id": self.session_id,
                "request_id": request_id or uuid.uuid4().hex,
                "message": user_prompt,
                "expected_version": expected_version,
                "case_id": case_id,
            },
        )
        return AgentResponse(**answer)
