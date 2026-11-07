from uuid import uuid4
from fastapi.testclient import TestClient
from main import app
from dependencies import get_service
from chat_handler_classes import AssistantService, PromptBuilder
from data_handler_classes import RulesRepo, ChatRepo
from llm_access_classes import LLMMockClient
import pytest


@pytest.fixture
def tst_client(tst_sess):
    service = AssistantService(RulesRepo(tst_sess), ChatRepo(tst_sess, 1, 10), LLMMockClient(), PromptBuilder("Mock prompt"))
    app.dependency_overrides[get_service] = lambda: service
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_send_message_returns_mock_reply(tst_client):
    response = tst_client.post(f"/chat/{uuid4()}", json={"text": "hi"})
    assert response.status_code == 200
    assert response.json() == {"role": "assistant", "content": "Mock reply"}