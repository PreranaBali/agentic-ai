"""Input schemas (what the API accepts).

NOTE: These are DASHBOARD schemas. They are not the official competition
observation/action formats, which are still pending.
"""
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Priority(str, Enum):
    low = "low"
    normal = "normal"
    high = "high"
    urgent = "urgent"


class RequestStatus(str, Enum):
    pending = "pending"
    needs_clarification = "needs_clarification"
    completed = "completed"
    escalated = "escalated"


class PartRequestCreate(BaseModel):
    requester_name: str = Field(min_length=1, max_length=100)
    equipment: str = Field(default="", max_length=200, description="Vehicle or machine the part is for")
    part_description: str = Field(min_length=3, max_length=1000)
    part_number: str = Field(default="", max_length=100)
    quantity: int = Field(default=1, ge=1, le=1000)
    priority: Priority = Priority.normal
    notes: str = Field(default="", max_length=2000)

    @field_validator("requester_name", "equipment", "part_description", "part_number", "notes")
    @classmethod
    def strip_text(cls, v: str) -> str:
        return v.strip()


class StatusUpdate(BaseModel):
    status: RequestStatus
    note: str = Field(default="", max_length=500)
