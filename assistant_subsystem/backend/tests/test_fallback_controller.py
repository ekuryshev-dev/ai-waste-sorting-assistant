from fastapi.testclient import TestClient
import pytest
from main import app
from dependencies import get_cv_service
from cv_fallback_classes import ImageFallbackClassifier
from chat_handler_classes import PromptBuilder
from data_handler_classes import RulesRepo
from llm_access_classes import LLMMockClient

GOOD = '{"material": "paper", "category": "recyclable", "instructions": "Blue bin."}'


@pytest.fixture
def tst_fallback_client(tst_sess):
    clf = ImageFallbackClassifier(LLMMockClient(GOOD), RulesRepo(tst_sess), PromptBuilder("Classify."))
    app.dependency_overrides[get_cv_service] = lambda: clf
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_fallback_returns_category_json(tst_fallback_client):
    response = tst_fallback_client.post(
        "/fallback/classify",
        files={"image": ("a.png", b"img", "image/png")},
        data={"region": "DE"},
    )
    assert response.status_code == 200
    assert response.json() == {"category": "recyclable", "material": "paper", "instructions": "Blue bin."}


def test_fallback_rejects_non_images(tst_fallback_client):
    response = tst_fallback_client.post(
        "/fallback/classify",
        files={"image": ("a.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 415