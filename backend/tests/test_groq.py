"""Groq service tests using a fake HTTP transport (no real network, no real key)."""
import asyncio

import httpx
import pytest

from app.config import Settings
from app.core.exceptions import (
    InvalidProviderResponseError,
    ProviderError,
    ProviderNotConfiguredError,
    ProviderRateLimitError,
    ProviderTimeoutError,
)
from app.services.groq_service import GroqService


def make_settings(**kw) -> Settings:
    base = dict(team_provider_key="test-key", team_model="test-model", groq_max_retries=1,
                database_path=":memory:", _env_file=None)
    base.update(kw)
    return Settings(**base)


def make_service(handler, **kw) -> GroqService:
    return GroqService(make_settings(**kw), transport=httpx.MockTransport(handler))


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    async def fast(_seconds):
        return None
    monkeypatch.setattr(asyncio, "sleep", fast)


OK_BODY = {"choices": [{"message": {"content": "hello"}}]}
MSGS = [{"role": "user", "content": "hi"}]


def test_chat_success_sends_key_and_model():
    seen = {}

    def handler(request: httpx.Request):
        seen["auth"] = request.headers["authorization"]
        seen["body"] = request.read().decode()
        return httpx.Response(200, json=OK_BODY)

    assert asyncio.run(make_service(handler).chat(MSGS)) == "hello"
    assert seen["auth"] == "Bearer test-key"
    assert '"model":"test-model"' in seen["body"].replace(" ", "")


def test_not_configured_raises():
    svc = make_service(lambda r: httpx.Response(200, json=OK_BODY), team_provider_key="")
    with pytest.raises(ProviderNotConfiguredError):
        asyncio.run(svc.chat(MSGS))


def test_rate_limit_retries_then_raises():
    calls = []

    def handler(request):
        calls.append(1)
        return httpx.Response(429, json={})

    with pytest.raises(ProviderRateLimitError):
        asyncio.run(make_service(handler).chat(MSGS))
    assert len(calls) == 2  # 1 try + 1 retry


def test_server_error_then_success():
    responses = [httpx.Response(500), httpx.Response(200, json=OK_BODY)]

    def handler(request):
        return responses.pop(0)

    assert asyncio.run(make_service(handler).chat(MSGS)) == "hello"


def test_bad_key_is_not_retried():
    calls = []

    def handler(request):
        calls.append(1)
        return httpx.Response(401, json={})

    with pytest.raises(ProviderError) as info:
        asyncio.run(make_service(handler).chat(MSGS))
    assert "API key" in info.value.message
    assert len(calls) == 1


def test_timeout_maps_to_provider_timeout():
    def handler(request):
        raise httpx.ConnectTimeout("slow")

    with pytest.raises(ProviderTimeoutError):
        asyncio.run(make_service(handler).chat(MSGS))


def test_unexpected_shape_raises():
    svc = make_service(lambda r: httpx.Response(200, json={"foo": 1}))
    with pytest.raises(InvalidProviderResponseError):
        asyncio.run(svc.chat(MSGS))


def test_list_models_sorted():
    body = {"data": [{"id": "b-model"}, {"id": "a-model"}]}
    svc = make_service(lambda r: httpx.Response(200, json=body))
    assert asyncio.run(svc.list_models()) == ["a-model", "b-model"]
