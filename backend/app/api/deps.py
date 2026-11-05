"""Shared service container, stored on app.state and injected into routes."""
from dataclasses import dataclass

from fastapi import Request

from app.agents.state_manager import AgentStateManager
from app.agents.workshop_agent import CompetitionAgentAdapter, WorkshopAdvisor
from app.config import Settings
from app.services.groq_service import GroqService
from app.services.workshop_service import WorkshopService


@dataclass
class Container:
    settings: Settings
    groq: GroqService
    workshop: WorkshopService
    state: AgentStateManager
    advisor: WorkshopAdvisor
    competition: CompetitionAgentAdapter


def get_container(request: Request) -> Container:
    return request.app.state.container
