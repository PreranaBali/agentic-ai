"""End-to-end API tests using FastAPI's TestClient and an in-memory database."""
import json

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.core.exceptions import ProviderRateLimitError
from app.main import create_app
from app.services.groq_service import GroqService

GOOD_REPLY = json.dumps({"summary": "Brake pad request.", "missing_information": [],
                         "clarifying_questions": [], "risk_flags": [],
                         "suggested_review_outcome": "ready_for_review"})
PAYLOAD = {"requester_name": "Sam", "equipment": "Forklift F-12", "part_description": "front left brake pad",
           "part_number": "BP-1001", "quantity": 2, "priority": "normal", "notes": ""}


class FakeGroq(GroqService):
    def __init__(self, cfg, error=None):
        super().__init__(cfg)
        self.error = error

    async def chat(self, messages, **kwargs):
        if self.error:
            raise self.error
        return GOOD_REPLY

    async def list_models(self):
        return ["test-model"]


def make_client(configured=True, error=None) -> TestClient:
    cfg = Settings(team_provider_key="secret-test-key-123" if configured else "", team_model="test-model" if configured else "",
                   database_path=":memory:", _env_file=None)
    return TestClient(create_app(cfg, groq=FakeGroq(cfg, error=error)))


@pytest.fixture
def client():
    return make_client()


def create(client, **overrides):
    return client.post("/api/requests", json={**PAYLOAD, **overrides})


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_create_get_list(client):
    created = create(client)
    assert created.status_code == 201
    rid = created.json()["id"]
    assert created.json()["status"] == "pending"
    detail = client.get(f"/api/requests/{rid}").json()
    assert detail["request"]["part_number"] == "BP-1001"
    assert detail["decisions"][0]["kind"] == "created"
    assert len(client.get("/api/requests").json()) == 1


def test_validation_errors(client):
    assert create(client, requester_name="").status_code == 422
    assert create(client, quantity=0).status_code == 422
    assert create(client, priority="whenever").status_code == 422


def test_not_found(client):
    r = client.get("/api/requests/999")
    assert r.status_code == 404 and r.json()["error"]["code"] == "not_found"


def test_status_update_logs_history(client):
    rid = create(client).json()["id"]
    r = client.patch(f"/api/requests/{rid}/status", json={"status": "escalated", "note": "odd part"})
    assert r.status_code == 200 and r.json()["status"] == "escalated"
    kinds = [d["kind"] for d in client.get(f"/api/requests/{rid}").json()["decisions"]]
    assert "status_change" in kinds
    assert client.patch(f"/api/requests/{rid}/status", json={"status": "dispatched"}).status_code == 422


def test_filter_and_search(client):
    a = create(client).json()["id"]
    create(client, part_description="hydraulic hose", part_number="HH-9")
    client.patch(f"/api/requests/{a}/status", json={"status": "completed"})
    assert len(client.get("/api/requests", params={"status": "completed"}).json()) == 1
    assert len(client.get("/api/requests", params={"search": "hydraulic"}).json()) == 1
    assert client.get("/api/requests", params={"status": "bogus"}).status_code == 422


def test_delete(client):
    rid = create(client).json()["id"]
    assert client.delete(f"/api/requests/{rid}").status_code == 204
    assert client.get(f"/api/requests/{rid}").status_code == 404


def test_stats(client):
    create(client)
    create(client)
    stats = client.get("/api/stats").json()
    assert stats["total"] == 2 and stats["pending"] == 2 and stats["escalated"] == 0


def test_analyze_with_groq_logs_decision(client):
    rid = create(client).json()["id"]
    r = client.post(f"/api/requests/{rid}/analyze")
    assert r.status_code == 200 and r.json()["groq_used"] is True
    decisions = client.get("/api/decisions", params={"request_id": rid}).json()
    assert decisions[0]["kind"] == "advisory_analysis" and decisions[0]["source"] == "groq+rules"


def test_analyze_rules_only_when_unconfigured():
    client = make_client(configured=False)
    rid = create(client, part_number="").json()["id"]
    r = client.post(f"/api/requests/{rid}/analyze").json()
    assert r["groq_used"] is False and r["suggested_review_outcome"] == "ask_for_clarification"


def test_analyze_provider_failure_returns_clean_error():
    client = make_client(error=ProviderRateLimitError("Groq rate limit reached. Try again shortly."))
    rid = create(client).json()["id"]
    r = client.post(f"/api/requests/{rid}/analyze")
    assert r.status_code == 429 and r.json()["error"]["code"] == "provider_rate_limited"
    assert client.get("/api/agent/status").json()["advisory_failures"] == 1


def test_agent_status_shows_competition_pending(client):
    data = client.get("/api/agent/status").json()
    assert data["competition_agent"]["state"] == "pending"


def test_provider_status(client):
    data = client.get("/api/provider/status").json()
    assert data["reachable"] is True and data["model_available"] is True
    assert "secret-test-key-123" not in json.dumps(data)  # key is never echoed back


def test_provider_status_not_configured():
    data = make_client(configured=False).get("/api/provider/status").json()
    assert data["configured"] is False
