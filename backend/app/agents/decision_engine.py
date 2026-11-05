"""Deterministic checks plus validation of the model's output.

Safety-relevant logic lives here in plain code, not in the LLM.
"""
import json
import re
from typing import Any

from app.core.exceptions import InvalidProviderResponseError

ALLOWED_OUTCOMES = {"ask_for_clarification", "ready_for_review", "needs_human_review"}
HIGH_QUANTITY = 50


def rule_checks(request: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Return (missing_information, risk_flags) in plain English."""
    missing: list[str] = []
    risks: list[str] = []
    if not request["equipment"].strip():
        missing.append("Equipment (vehicle or machine) is not specified.")
    if not request["part_number"].strip():
        missing.append("No part number was given.")
    if len(request["part_description"].split()) < 3:
        missing.append("Part description is very short and may be ambiguous.")
    if request["quantity"] >= HIGH_QUANTITY:
        risks.append(f"Unusually high quantity requested ({request['quantity']}).")
    if request["priority"] == "urgent":
        risks.append("Marked urgent: confirm details quickly.")
    return missing, risks


def _as_str_list(value: Any, limit: int = 8) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(v).strip()[:300] for v in value if str(v).strip()][:limit]


def parse_model_output(text: str) -> dict[str, Any]:
    """Extract and validate the JSON object returned by the model."""
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end <= start:
        raise InvalidProviderResponseError("Model reply did not contain a JSON object.")
    try:
        data = json.loads(cleaned[start:end + 1])
    except json.JSONDecodeError:
        raise InvalidProviderResponseError("Model reply was not valid JSON.")
    if not isinstance(data, dict) or not isinstance(data.get("summary"), str) or not data["summary"].strip():
        raise InvalidProviderResponseError("Model reply had no usable summary.")
    outcome = data.get("suggested_review_outcome")
    if outcome not in ALLOWED_OUTCOMES:
        outcome = "needs_human_review"  # safe default if the model drifts
    return {
        "summary": data["summary"].strip()[:600],
        "missing_information": _as_str_list(data.get("missing_information")),
        "clarifying_questions": _as_str_list(data.get("clarifying_questions")),
        "risk_flags": _as_str_list(data.get("risk_flags")),
        "suggested_review_outcome": outcome,
    }


def rules_only_outcome(missing: list[str]) -> str:
    return "ask_for_clarification" if missing else "ready_for_review"


def merge_with_rules(model: dict[str, Any], missing: list[str], risks: list[str]) -> dict[str, Any]:
    """Rules always win: never let the model soften a deterministic finding."""
    merged = dict(model)
    for m in missing:
        if m not in merged["missing_information"]:
            merged["missing_information"].append(m)
    for r in risks:
        if r not in merged["risk_flags"]:
            merged["risk_flags"].append(r)
    if missing and merged["suggested_review_outcome"] == "ready_for_review":
        merged["suggested_review_outcome"] = "ask_for_clarification"
    return merged
