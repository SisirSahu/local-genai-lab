import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from genai_app.api.chat import router
from genai_app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)
    yield


app = FastAPI(
    title="Local GenAI API",
    description="Stateless chat using a locally installed Ollama model.",
    lifespan=lifespan,
)
app.include_router(router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    """Application liveness, not Ollama readiness."""
    return {"status": "ok"}
