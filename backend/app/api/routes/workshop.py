"""Part request management, advisory analysis, decision history and agent status."""
from typing import Optional

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.deps import Container, get_container
from app.schemas.request import PartRequestCreate, RequestStatus, StatusUpdate
from app.schemas.response import (
    AdvisoryAnalysis,
    AgentStatusOut,
    DecisionOut,
    PartRequestOut,
    RequestDetailOut,
    StatsOut,
)

router = APIRouter(prefix="/api", tags=["workshop"])


@router.post("/requests", response_model=PartRequestOut, status_code=status.HTTP_201_CREATED)
def create_request(body: PartRequestCreate, c: Container = Depends(get_container)):
    return c.workshop.create_request(body)


@router.get("/requests", response_model=list[PartRequestOut])
def list_requests(
    status: Optional[RequestStatus] = None,
    search: Optional[str] = Query(default=None, max_length=100),
    c: Container = Depends(get_container),
):
    return c.workshop.list_requests(status.value if status else None, search)


@router.get("/requests/{request_id}", response_model=RequestDetailOut)
def get_request(request_id: int, c: Container = Depends(get_container)):
    return {
        "request": c.workshop.get_request(request_id),
        "decisions": c.workshop.list_decisions(request_id),
    }


@router.patch("/requests/{request_id}/status", response_model=PartRequestOut)
def update_status(request_id: int, body: StatusUpdate, c: Container = Depends(get_container)):
    return c.workshop.update_status(request_id, body.status, body.note)


@router.delete("/requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_request(request_id: int, c: Container = Depends(get_container)):
    c.workshop.delete_request(request_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/requests/{request_id}/analyze", response_model=AdvisoryAnalysis)
async def analyze_request(request_id: int, c: Container = Depends(get_container)):
    request = c.workshop.get_request(request_id)
    analysis = await c.advisor.analyze(request)
    c.workshop.add_decision(
        request_id,
        "advisory_analysis",
        "groq+rules" if analysis.groq_used else "rules",
        analysis.summary,
        analysis.model_dump(),
    )
    return analysis


@router.get("/decisions", response_model=list[DecisionOut])
def list_decisions(
    request_id: Optional[int] = None,
    limit: int = Query(default=100, ge=1, le=500),
    c: Container = Depends(get_container),
):
    return c.workshop.list_decisions(request_id, limit)


@router.get("/stats", response_model=StatsOut)
def stats(c: Container = Depends(get_container)):
    return c.workshop.stats()


@router.get("/agent/status", response_model=AgentStatusOut)
def agent_status(c: Container = Depends(get_container)):
    return {**c.state.snapshot(), "competition_agent": c.competition.status()}
