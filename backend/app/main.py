"""FastAPI entry point. Run with: uvicorn app.main:app --reload"""
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.agents.state_manager import AgentStateManager
from app.agents.workshop_agent import CompetitionAgentAdapter, WorkshopAdvisor
from app.api.deps import Container
from app.api.routes import health, workshop
from app.config import Settings, get_settings
from app.core.exceptions import AppError
from app.core.security import redact
from app.services.groq_service import GroqService
from app.services.workshop_service import WorkshopService
from app.utils.logger import get_logger, setup_logging

log = get_logger(__name__)


def create_app(settings: Optional[Settings] = None, groq: Optional[GroqService] = None) -> FastAPI:
    settings = settings or get_settings()
    setup_logging(settings.log_level)

    groq = groq or GroqService(settings)
    state = AgentStateManager()
    container = Container(
        settings=settings,
        groq=groq,
        workshop=WorkshopService(settings.database_path),
        state=state,
        advisor=WorkshopAdvisor(groq, state),
        competition=CompetitionAgentAdapter(),
    )

    app = FastAPI(title="Workshop Parts Desk API", version=health.APP_VERSION)
    app.state.container = container

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError):
        return JSONResponse(status_code=exc.status_code,
                            content={"error": {"code": exc.code, "message": redact(exc.message)}})

    @app.exception_handler(Exception)
    async def unhandled_handler(_: Request, exc: Exception):
        log.exception("Unhandled error: %s", type(exc).__name__)
        return JSONResponse(status_code=500,
                            content={"error": {"code": "internal_error", "message": "Unexpected server error."}})

    app.include_router(health.router)
    app.include_router(workshop.router)

    log.info("Groq configured: %s (model: %s)", settings.groq_configured, settings.team_model or "-")
    return app


app = create_app()
