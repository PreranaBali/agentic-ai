"""Helpers that keep secrets out of logs and responses."""
import re

_BEARER = re.compile(r"(Bearer\s+)[A-Za-z0-9._\-]+", re.IGNORECASE)
_GROQ_KEY = re.compile(r"gsk_[A-Za-z0-9]+")


def mask_secret(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-2:]}"


def redact(text: str) -> str:
    """Remove anything that looks like an API key from text."""
    text = _BEARER.sub(r"\1[REDACTED]", text)
    return _GROQ_KEY.sub("[REDACTED]", text)
