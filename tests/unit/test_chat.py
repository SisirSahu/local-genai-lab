from unittest.mock import AsyncMock, patch

import pytest
from langchain_core.messages import AIMessage
from pydantic import ValidationError

from genai_app.config import Settings
from genai_app.schemas.chat import ChatRequest
from genai_app.services.chat import ChatService, InvalidModelResponseError


def test_prompt_is_trimmed():
    assert ChatRequest(prompt=" hello ").prompt == "hello"


@pytest.mark.parametrize("prompt", ["", "  ", "x" * 16001])
def test_invalid_prompt(prompt):
    with pytest.raises(ValidationError):
        ChatRequest(prompt=prompt)


def test_invalid_timeout():
    with pytest.raises(ValidationError):
        Settings(ollama_timeout_seconds=0)


def test_model_invocation():
    import asyncio

    with patch("genai_app.services.chat.ChatOllama") as model:
        model.return_value.ainvoke = AsyncMock(return_value=AIMessage(content="Hello"))
        service = ChatService(Settings())
        response = asyncio.run(service.chat("Hi"))
        assert response.response == "Hello"
        assert response.model == "qwen3:8b"
        model.return_value.ainvoke.assert_awaited_once_with("Hi")
        assert model.call_args.kwargs["client_kwargs"]["trust_env"] is False


def test_empty_model_response():
    import asyncio

    with patch("genai_app.services.chat.ChatOllama") as model:
        model.return_value.ainvoke = AsyncMock(return_value=AIMessage(content=""))
        service = ChatService(Settings())
        with pytest.raises(InvalidModelResponseError):
            asyncio.run(service.chat("Hi"))
