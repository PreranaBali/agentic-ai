"""Prompts for the ADVISORY assistant (not the official competition agent)."""
import json
from typing import Any

SYSTEM_PROMPT = """You are an assistant for a workshop parts desk. You review one parts request \
and give ADVISORY notes to a human operator. You do not dispatch parts or take actions.

Rules:
- Use only the facts given in the request. Never invent part numbers, stock levels, prices or compatibility.
- If something is unclear, say it is unclear.
- Reply with ONE JSON object and nothing else (no markdown), with exactly these keys:
  "summary": string (1-2 sentences),
  "missing_information": array of short strings,
  "clarifying_questions": array of short questions for the requester,
  "risk_flags": array of short strings,
  "suggested_review_outcome": one of "ask_for_clarification", "ready_for_review", "needs_human_review"
"""


def build_user_prompt(request: dict[str, Any], rule_findings: list[str]) -> str:
    """rule_findings = missing information and risk flags found by plain code."""
    facts = {
        "requester": request["requester_name"],
        "equipment": request["equipment"] or "(not provided)",
        "part_description": request["part_description"],
        "part_number": request["part_number"] or "(not provided)",
        "quantity": request["quantity"],
        "priority": request["priority"],
        "notes": request["notes"] or "(none)",
    }
    return (
        "Parts request:\n" + json.dumps(facts, indent=2)
        + "\n\nAutomatic checks already found:\n"
        + ("\n".join(f"- {f}" for f in rule_findings) if rule_findings else "- nothing")
    )
