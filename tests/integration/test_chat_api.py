import httpx
import pytest
from ollama import ResponseError

from genai_app.schemas.chat import ChatResponse
from genai_app.services.chat import InvalidModelResponseError


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_chat(client, service):
    service.chat.return_value = ChatResponse(model="qwen3:8b", response="Hello")
    response = client.post("/api/chat", json={"prompt": " Hi "})
    assert response.status_code == 200
    assert response.json() == {"model": "qwen3:8b", "response": "Hello"}
    service.chat.assert_awaited_once_with("Hi")


@pytest.mark.parametrize(
    "body", [{}, {"prompt": " "}, {"prompt": "x", "unexpected": True}]
)
def test_validation(client, service, body):
    assert client.post("/api/chat", json=body).status_code == 422
    service.chat.assert_not_awaited()


@pytest.mark.parametrize(
    ("error", "status"),
    [
        (httpx.ConnectError("unavailable"), 503),
        (ConnectionError("unavailable"), 503),
        (httpx.ReadTimeout("timeout"), 504),
        (ResponseError("missing model", 404), 502),
        (ResponseError("internal failure", 500), 502),
        (InvalidModelResponseError("empty"), 502),
    ],
)
def test_upstream_errors(client, service, error, status):
    service.chat.side_effect = error
    response = client.post("/api/chat", json={"prompt": "Hello"})
    assert response.status_code == status
    assert response.json()["detail"]
