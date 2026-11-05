"""Groq (OpenAI-compatible) client. The API key never leaves this module."""
import asyncio
from typing import Optional

import httpx

from app.config import Settings
from app.core.exceptions import (
    InvalidProviderResponseError,
    ProviderError,
    ProviderNotConfiguredError,
    ProviderRateLimitError,
    ProviderTimeoutError,
)
from app.utils.logger import get_logger

log = get_logger(__name__)


def _fatal(message: str) -> ProviderError:
    """A provider error that retrying cannot fix."""
    err = ProviderError(message)
    err.fatal = True
    return err


class GroqService:
    def __init__(self, settings: Settings, transport: Optional[httpx.AsyncBaseTransport] = None):
        self.settings = settings
        self._transport = transport  # lets tests inject a fake transport

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.settings.team_provider_key}",
            "Content-Type": "application/json",
        }

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=self.settings.groq_timeout_seconds, transport=self._transport)

    def _require_config(self) -> None:
        if not self.settings.groq_configured:
            raise ProviderNotConfiguredError(
                "Groq is not configured. Set TEAM_PROVIDER_KEY and TEAM_MODEL in backend/.env."
            )

    async def chat(self, messages: list[dict], temperature: float = 0.1, max_tokens: int = 600) -> str:
        """Send a chat completion and return the assistant text."""
        self._require_config()
        payload = {
            "model": self.settings.team_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        attempts = self.settings.groq_max_retries + 1
        last_error: Optional[Exception] = None
        for attempt in range(1, attempts + 1):
            try:
                async with self._client() as client:
                    resp = await client.post(
                        self.settings.team_provider_url, json=payload, headers=self._headers()
                    )
                if resp.status_code == 429:
                    raise ProviderRateLimitError("Groq rate limit reached. Try again shortly.")
                if resp.status_code in (401, 403):
                    raise _fatal("Groq rejected the API key (check TEAM_PROVIDER_KEY).")
                if resp.status_code == 404:
                    raise _fatal("Groq returned 404. Check TEAM_MODEL and TEAM_PROVIDER_URL.")
                if resp.status_code >= 500:
                    raise ProviderError(f"Groq server error ({resp.status_code}).")
                if resp.status_code >= 400:
                    raise _fatal(f"Groq request failed ({resp.status_code}). Check TEAM_MODEL.")
                return self._extract_text(resp)
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                last_error = ProviderTimeoutError("Could not reach Groq in time.")
                log.warning("Groq network issue on attempt %d/%d: %s", attempt, attempts, type(exc).__name__)
            except (ProviderRateLimitError, ProviderError) as exc:
                if getattr(exc, "fatal", False) or isinstance(exc, InvalidProviderResponseError):
                    raise  # retrying will not help
                last_error = exc
                log.warning("Groq issue on attempt %d/%d: %s", attempt, attempts, exc.message)
            if attempt < attempts:
                await asyncio.sleep(min(2 ** (attempt - 1), 4))
        assert last_error is not None
        raise last_error

    @staticmethod
    def _extract_text(resp: httpx.Response) -> str:
        try:
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError):
            raise InvalidProviderResponseError("Groq returned an unexpected response shape.")
        if not isinstance(text, str) or not text.strip():
            raise InvalidProviderResponseError("Groq returned an empty answer.")
        return text

    async def list_models(self) -> list[str]:
        if not self.settings.team_provider_key:
            raise ProviderNotConfiguredError("TEAM_PROVIDER_KEY is not set in backend/.env.")
        try:
            async with self._client() as client:
                resp = await client.get(self.settings.groq_models_url, headers=self._headers())
        except (httpx.TimeoutException, httpx.TransportError):
            raise ProviderTimeoutError("Could not reach Groq in time.")
        if resp.status_code in (401, 403):
            raise ProviderError("Groq rejected the API key (check TEAM_PROVIDER_KEY).")
        if resp.status_code >= 400:
            raise ProviderError(f"Groq models request failed ({resp.status_code}).")
        try:
            return sorted(m["id"] for m in resp.json()["data"])
        except (ValueError, KeyError, TypeError):
            raise InvalidProviderResponseError("Groq returned an unexpected models response.")
