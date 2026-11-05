"""Tests for the deterministic rules and the advisory agent."""
import asyncio
import json

import pytest

from app.agents import decision_engine as engine
from app.agents.state_manager import AgentStateManager
from app.agents.workshop_agent import CompetitionAgentAdapter, WorkshopAdvisor
from app.config import Settings
from app.core.exceptions import InvalidProviderResponseError, ProtocolPendingError, ProviderError
from app.services.groq_service import GroqService


def settings(**kw) -> Settings:
    base = dict(team_provider_key="k", team_model="m", database_path=":memory:", _env_file=None)
    base.update(kw)
    return Settings(**base)


class FakeGroq(GroqService):
    def __init__(self, cfg, reply=None, error=None):
        super().__init__(cfg)
        self.reply, self.error = reply, error

    async def chat(self, messages, **kwargs):
        if self.error:
            raise self.error
        return self.reply


def sample_request(**kw):
    base = {"id": 1, "requester_name": "Sam", "equipment": "Forklift F-12", "part_description": "front left brake pad",
            "part_number": "BP-1001", "quantity": 2, "priority": "normal", "notes": ""}
    base.update(kw)
    return base


def test_rules_flag_missing_fields():
    missing, risks = engine.rule_checks(sample_request(equipment="", part_number="", part_description="brake",
                                                      quantity=60, priority="urgent"))
    assert len(missing) == 3 and len(risks) == 2
    assert engine.rules_only_outcome(missing) == "ask_for_clarification"


def test_rules_complete_request_is_clean():
    missing, risks = engine.rule_checks(sample_request())
    assert missing == [] and risks == []
    assert engine.rules_only_outcome(missing) == "ready_for_review"


def test_parse_accepts_fenced_json_and_fixes_unknown_outcome():
    text = "```json\n" + json.dumps({"summary": "ok", "suggested_review_outcome": "dispatch_now"}) + "\n```"
    parsed = engine.parse_model_output(text)
    assert parsed["suggested_review_outcome"] == "needs_human_review"


@pytest.mark.parametrize("bad", ["no json", "{not json}", '{"summary": ""}', "[1,2]"])
def test_parse_rejects_bad_output(bad):
    with pytest.raises(InvalidProviderResponseError):
        engine.parse_model_output(bad)


def test_merge_never_softens_rules():
    model = engine.parse_model_output(json.dumps({"summary": "fine", "suggested_review_outcome": "ready_for_review"}))
    missing, risks = engine.rule_checks(sample_request(part_number=""))
    merged = engine.merge_with_rules(model, missing, risks)
    assert merged["suggested_review_outcome"] == "ask_for_clarification"
    assert "No part number was given." in merged["missing_information"]


def test_advisor_with_groq_success():
    reply = json.dumps({"summary": "Brake pad for forklift.", "missing_information": [],
                        "clarifying_questions": ["Which side?"], "risk_flags": [],
                        "suggested_review_outcome": "ready_for_review"})
    state = AgentStateManager()
    advisor = WorkshopAdvisor(FakeGroq(settings(), reply=reply), state)
    result = asyncio.run(advisor.analyze(sample_request()))
    assert result.groq_used and result.model == "m"
    assert state.snapshot()["advisory_runs"] == 1


def test_advisor_rules_only_when_not_configured():
    state = AgentStateManager()
    advisor = WorkshopAdvisor(FakeGroq(settings(team_provider_key="")), state)
    result = asyncio.run(advisor.analyze(sample_request(part_number="")))
    assert not result.groq_used
    assert result.suggested_review_outcome == "ask_for_clarification"


def test_advisor_records_failure_and_reraises():
    state = AgentStateManager()
    advisor = WorkshopAdvisor(FakeGroq(settings(), error=ProviderError("boom")), state)
    with pytest.raises(ProviderError):
        asyncio.run(advisor.analyze(sample_request()))
    snap = state.snapshot()
    assert snap["advisory_failures"] == 1 and snap["recent_events"][0]["ok"] is False


def test_competition_agent_is_pending():
    adapter = CompetitionAgentAdapter()
    assert adapter.status()["state"] == "pending"
    with pytest.raises(ProtocolPendingError):
        adapter.run()
