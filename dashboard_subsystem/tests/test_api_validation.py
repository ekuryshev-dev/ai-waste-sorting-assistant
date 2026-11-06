import pytest

from pydantic import ValidationError
from waste_analytics.api import NewRecord
from fastapi.testclient import TestClient
from waste_analytics.api import app

def test_invalid_category():
    with pytest.raises(ValidationError):
        NewRecord(
            item="Plastic bottle",
            category="plastic",
            region_code="Dortmund"
        )


def test_missing_category():
    with pytest.raises(ValidationError):
        NewRecord(
            item="Plastic bottle",
            region_code="Dortmund"
        )

def test_api_invalid_category():
    client = TestClient(app)

    response = client.post(
        "/analytics/records",
        json={
            "item": "Plastic bottle",
            "category": "plastic",
            "region_code": "Dortmund"
        }
    )

    assert response.status_code == 422


def test_api_missing_category():
    client = TestClient(app)

    response = client.post(
        "/analytics/records",
        json={
            "item": "Plastic bottle",
            "region_code": "Dortmund"
        }
    )

    assert response.status_code == 422

def test_api_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200

