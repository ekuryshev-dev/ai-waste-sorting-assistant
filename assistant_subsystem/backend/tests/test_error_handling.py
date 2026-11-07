from uuid import uuid4
from fastapi.testclient import TestClient
from chat_handler_classes import AssistantService, PromptBuilder
from cv_fallback_classes import ImageFallbackClassifier
from data_handler_classes import Category, ChatRepo, RulesRepo
from dependencies import get_service
from errors import LLMTimeoutError
from llm_access_classes import LLMClientInter
from main import app


class FailingClient(LLMClientInter):
    def converse(self, messages):
        raise LLMTimeoutError("timeout")


def test_chat_returns_504_on_timeout(tst_sess):
    service = AssistantService(RulesRepo(tst_sess), ChatRepo(tst_sess, 1, 10), FailingClient(), PromptBuilder("Mock prompt"))
    app.dependency_overrides[get_service] = lambda: service
    response = TestClient(app).post(f"/chat/{uuid4()}", json={"text": "hi"})
    app.dependency_overrides.clear()
    assert response.status_code == 504


def test_fallback_returns_unknown_on_error(tst_sess):
    clf = ImageFallbackClassifier(FailingClient(), RulesRepo(tst_sess), PromptBuilder("Mock prompt"))
    assert clf.classify(b"img").category == Category.unknown