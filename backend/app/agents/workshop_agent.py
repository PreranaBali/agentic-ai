"""Advisory agent used by the dashboard, plus the pending competition-agent slot."""
from typing import Any

from app.agents import decision_engine as engine
from app.agents.prompt_manager import SYSTEM_PROMPT, build_user_prompt
from app.agents.state_manager import AgentStateManager
from app.core.exceptions import AppError, ProtocolPendingError
from app.schemas.response import AdvisoryAnalysis
from app.services.groq_service import GroqService
from app.utils.logger import get_logger

log = get_logger(__name__)

COMPETITION_AGENT_STATUS = {
    "state": "pending",
    "message": "Official Workshop Parts Desk protocol (actions, observations, scoring) has not been "
               "provided yet. The official agent will live in competition/solution.py.",
}


class WorkshopAdvisor:
    def __init__(self, groq: GroqService, state: AgentStateManager):
        self.groq = groq
        self.state = state

    async def analyze(self, request: dict[str, Any]) -> AdvisoryAnalysis:
        missing, risks = engine.rule_checks(request)
        findings = missing + risks

        if not self.groq.settings.groq_configured:
            self.state.record(request["id"], True, False, "Rules-only analysis (Groq not configured).")
            return AdvisoryAnalysis(
                summary="Rules-only review (Groq is not configured).",
                missing_information=missing,
                clarifying_questions=[],
                risk_flags=risks,
                suggested_review_outcome=engine.rules_only_outcome(missing),
                groq_used=False,
            )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(request, findings)},
        ]
        try:
            text = await self.groq.chat(messages)
            parsed = engine.parse_model_output(text)
        except AppError as exc:
            self.state.record(request["id"], False, True, exc.message)
            raise
        merged = engine.merge_with_rules(parsed, missing, risks)
        self.state.record(request["id"], True, True, "Groq analysis completed.")
        return AdvisoryAnalysis(**merged, groq_used=True, model=self.groq.settings.team_model)


class CompetitionAgentAdapter:
    """Placeholder. Implemented only after the official protocol is provided."""

    def status(self) -> dict[str, Any]:
        return dict(COMPETITION_AGENT_STATUS)

    def run(self, *_args, **_kwargs):
        raise ProtocolPendingError(COMPETITION_AGENT_STATUS["message"])
