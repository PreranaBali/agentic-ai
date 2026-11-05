"""Health and Groq connection status."""
from fastapi import APIRouter, Depends

from app.api.deps import Container, get_container
from app.core.exceptions import AppError
from app.core.security import redact
from app.schemas.response import HealthOut, ModelsOut, ProviderStatusOut

router = APIRouter(prefix="/api", tags=["health"])
APP_VERSION = "0.1.0"


@router.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    return HealthOut(status="ok", version=APP_VERSION)


@router.get("/provider/status", response_model=ProviderStatusOut)
async def provider_status(c: Container = Depends(get_container)) -> ProviderStatusOut:
    s = c.settings
    base = dict(model=s.team_model, provider_url=s.team_provider_url)
    if not s.team_provider_key:
        return ProviderStatusOut(configured=False, message="TEAM_PROVIDER_KEY is not set in backend/.env.", **base)
    try:
        models = await c.groq.list_models()
    except AppError as exc:
        return ProviderStatusOut(configured=s.groq_configured, reachable=False, message=redact(exc.message), **base)
    if not s.team_model:
        return ProviderStatusOut(configured=False, reachable=True,
                                 message="Key works. Set TEAM_MODEL to one of the available models.", **base)
    available = s.team_model in models
    msg = "Connected." if available else f"Connected, but model '{s.team_model}' is not in your available models."
    return ProviderStatusOut(configured=True, reachable=True, model_available=available, message=msg, **base)


@router.get("/provider/models", response_model=ModelsOut)
async def provider_models(c: Container = Depends(get_container)) -> ModelsOut:
    return ModelsOut(models=await c.groq.list_models())
