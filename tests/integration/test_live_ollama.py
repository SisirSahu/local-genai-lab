import os

import pytest
from fastapi.testclient import TestClient

from genai_app.main import app


@pytest.mark.live
@pytest.mark.skipif(
    os.getenv("RUN_LIVE_TESTS") != "1", reason="Set RUN_LIVE_TESTS=1 to call Ollama"
)
def test_live_chat():
    with TestClient(app) as client:
        response = client.post(
            "/api/chat", json={"prompt": "Reply with a short greeting in English."}
        )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["model"]
    assert isinstance(body["response"], str)
    assert body["response"].strip()
