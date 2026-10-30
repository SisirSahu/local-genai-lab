from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from genai_app.main import app
from genai_app.services.chat import ChatService, get_chat_service


@pytest.fixture
def service():
    return AsyncMock(spec=ChatService)


@pytest.fixture
def client(service):
    app.dependency_overrides[get_chat_service] = lambda: service
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
