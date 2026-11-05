"""Output schemas (what the API returns)."""
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.schemas.request import Priority, RequestStatus


class PartRequestOut(BaseModel):
    id: int
    requester_name: str
    equipment: str
    part_description: str
    part_number: str
    quantity: int
    priority: Priority
    notes: str
    status: RequestStatus
    created_at: str
    updated_at: str


class DecisionOut(BaseModel):
    id: int
    request_id: int
    kind: str  # "advisory_analysis" | "status_change" | "created"
    source: str  # "groq+rules" | "rules" | "operator" | "system"
    summary: str
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class RequestDetailOut(BaseModel):
    request: PartRequestOut
    decisions: list[DecisionOut]


class StatsOut(BaseModel):
    total: int
    pending: int
    needs_clarification: int
    completed: int
    escalated: int


class AdvisoryAnalysis(BaseModel):
    """Advisory output of the dashboard assistant. NOT an official competition action."""
    summary: str
    missing_information: list[str] = Field(default_factory=list)
    clarifying_questions: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    suggested_review_outcome: str  # ask_for_clarification | ready_for_review | needs_human_review
    groq_used: bool
    model: Optional[str] = None
    disclaimer: str = (
        "Advisory only. This is not the official competition agent; its protocol is pending."
    )


class HealthOut(BaseModel):
    status: str
    version: str


class ProviderStatusOut(BaseModel):
    configured: bool
    reachable: Optional[bool] = None
    model: str
    model_available: Optional[bool] = None
    provider_url: str
    message: str


class ModelsOut(BaseModel):
    models: list[str]


class AgentStatusOut(BaseModel):
    advisory_runs: int
    advisory_failures: int
    last_run_at: Optional[str]
    recent_events: list[dict[str, Any]]
    competition_agent: dict[str, Any]
