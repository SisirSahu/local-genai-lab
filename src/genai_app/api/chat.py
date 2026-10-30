import logging
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException
from ollama import ResponseError

from genai_app.schemas.chat import ChatRequest, ChatResponse
from genai_app.services.chat import (
    ChatService,
    InvalidModelResponseError,
    get_chat_service,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: Annotated[ChatService, Depends(get_chat_service)],
) -> ChatResponse:
    try:
        return await service.chat(request.prompt)
    except httpx.TimeoutException as exc:
        logger.warning("Ollama request timed out")
        raise HTTPException(504, "Ollama request timed out. Try again.") from exc
    except (httpx.RequestError, ConnectionError) as exc:
        logger.warning("Ollama connection failed: %s", type(exc).__name__)
        raise HTTPException(
            503, "Cannot connect to Ollama. Ensure Ollama is running."
        ) from exc
    except ResponseError as exc:
        logger.warning("Ollama rejected request with status %s", exc.status_code)
        detail = (
            "Model not found. Download the configured model using ollama pull."
            if exc.status_code == 404
            else "Ollama could not complete the request. Check the Ollama logs."
        )
        raise HTTPException(502, detail) from exc
    except InvalidModelResponseError as exc:
        logger.warning("Ollama returned an empty or unsupported response")
        raise HTTPException(502, "Ollama returned no usable text.") from exc
