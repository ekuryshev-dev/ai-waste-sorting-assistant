import json
from io import BytesIO
from pathlib import Path

import pytest
from fastapi import HTTPException, UploadFile
from starlette.datastructures import Headers
from sqlalchemy import inspect

from classification_subsystem.backend.src.analytics_client import AnalyticsClient
from classification_subsystem.backend.src.class_mapping import ClassMapping
from classification_subsystem.backend.src.conveyor_pipeline import (
    ConfidenceFilter, MaterialRouter, PredictionEvent, PredictionStream,
)
from classification_subsystem.backend.src.engine import DisposalRecommendationEngine
from classification_subsystem.backend.src.errors import InvalidImageError, RuleNotFoundError
from classification_subsystem.backend.src.fallback_client import AssistantFallbackClient
from classification_subsystem.backend.src.image_processing import ImageProcessor
from classification_subsystem.backend.src.main import recommend
from classification_subsystem.backend.src.models import (
    ClassificationResult, FallbackResult, ImageQuery,
)
from classification_subsystem.backend.src.regional_rules import RegionalRulesService
from classification_subsystem.backend.src.wasteclassifier import WasteClassifier


BACKEND = Path(__file__).resolve().parents[1]
PHOTO = (Path(__file__).parent / "fixtures" / "battery1.jpg").read_bytes()


class FakeClassifier:
    def __init__(self, label="battery", confidence=0.99):
        self.result = ClassificationResult(label, confidence, "cv")

    def classify(self, image):
        assert image.size == (224, 224) and image.mode == "RGB"
        return self.result


class FakeFallback:
    def __init__(self, material="battery"):
        self.result = FallbackResult(material)
        self.calls = 0

    def classify(self, image, mime_type, region, materials):
        self.calls += 1
        assert image == PHOTO
        assert mime_type == "image/jpeg"
        assert region == "Dortmund"
        assert material_list_contains_expected_values(materials)
        return self.result


def material_list_contains_expected_values(materials):
    return "battery" in materials and "paper" in materials and len(materials) == 12


class FakeStatistics:
    def __init__(self):
        self.records = []

    def record(self, waste_class, category, region):
        self.records.append((waste_class, category, region))


@pytest.fixture
def rules(tmp_path):
    service = RegionalRulesService(f"sqlite:///{tmp_path / 'rules.db'}")
    service.create_tables()
    assert service.import_json(BACKEND / "regional_rules_2026.json") == 120
    return service


@pytest.fixture
def make_engine(rules):
    def build(classifier=None, fallback=None, statistics=None):
        return DisposalRecommendationEngine(
            classifier or FakeClassifier(), rules,
            ClassMapping(BACKEND / "class_mapping.json"), ImageProcessor(),
            fallback=fallback, statistics=statistics,
        )
    return build


def test_high_confidence_uses_cv_and_regional_rule(make_engine):
    fallback = FakeFallback()
    statistics = FakeStatistics()
    outcome = make_engine(fallback=fallback, statistics=statistics).get_recommendation(
        ImageQuery(PHOTO, "Dortmund")
    )
    assert outcome.status == "ok"
    assert outcome.classification == ClassificationResult("battery", 0.99, "cv")
    assert outcome.category == "recyclable"
    assert "Never put" in outcome.message
    assert fallback.calls == 0
    assert statistics.records == [("battery", "recyclable", "Dortmund")]


def test_low_confidence_uses_ai_material_and_regional_instructions(make_engine):
    statistics = FakeStatistics()
    outcome = make_engine(
        FakeClassifier("trash", 0.4), FakeFallback("battery"), statistics
    ).get_recommendation(ImageQuery(PHOTO, "Dortmund"))
    assert outcome.classification == ClassificationResult("battery", None, "ai")
    assert outcome.category == "recyclable"
    assert "battery collection box" in outcome.message
    assert statistics.records == [("battery", "recyclable", "Dortmund")]


@pytest.mark.parametrize("material", [None, "unmapped item"])
def test_ai_cannot_identify_item_requests_new_photo(make_engine, material):
    statistics = FakeStatistics()
    outcome = make_engine(
        FakeClassifier(confidence=0.2), FakeFallback(material), statistics
    ).get_recommendation(ImageQuery(PHOTO, "Dortmund"))
    assert outcome.status == "retry_photo"
    assert outcome.classification is None
    assert outcome.category == "unknown"
    assert statistics.records == []


def test_low_confidence_without_fallback_requests_new_photo(make_engine):
    outcome = make_engine(FakeClassifier(confidence=0.2)).get_recommendation(
        ImageQuery(PHOTO, "Dortmund")
    )
    assert outcome.status == "retry_photo"


def test_invalid_and_oversized_images_are_rejected(make_engine):
    engine = make_engine()
    with pytest.raises(InvalidImageError):
        engine.get_recommendation(ImageQuery(b"not an image", "Dortmund"))
    with pytest.raises(InvalidImageError):
        engine.get_recommendation(ImageQuery(PHOTO, "Dortmund", "image/gif"))
    engine.image_processor.max_bytes = len(PHOTO) - 1
    with pytest.raises(InvalidImageError):
        engine.get_recommendation(ImageQuery(PHOTO, "Dortmund"))


def test_unsupported_region_is_rejected(make_engine):
    with pytest.raises(ValueError, match="Unsupported region"):
        make_engine().get_recommendation(ImageQuery(PHOTO, "Unknown region"))


def test_missing_rule_never_becomes_recommendation(make_engine):
    with pytest.raises(RuleNotFoundError):
        make_engine(FakeClassifier("not-in-database")).rules_service.get_rule(
            "not-in-database", "Dortmund"
        )


def test_new_region_can_be_imported_without_code_change(rules, tmp_path):
    path = tmp_path / "new_region.json"
    path.write_text(json.dumps([{
        "region": "New demo region", "material": "battery", "category": "recyclable",
        "instructions": "Take batteries to the collection box."
    }]), encoding="utf-8")
    rules.import_json(path)
    assert "New demo region" in rules.list_regions()
    assert rules.get_rule("battery", "New demo region").instructions == "Take batteries to the collection box."
    path.write_text(path.read_text(encoding="utf-8").replace(
        "collection box", "Battery point"
    ), encoding="utf-8")
    rules.import_json(path)
    assert rules.get_rule("battery", "New demo region").instructions == "Take batteries to the Battery point."


def test_classification_rule_table_has_expected_columns(rules):
    columns = {column["name"] for column in inspect(rules.engine).get_columns("classification_recycling_rules")}
    assert columns == {"id", "region", "material", "category", "instructions"}


def test_regional_records_have_source_for_every_pair():
    records = json.loads((BACKEND / "regional_rules_2026.json").read_text(encoding="utf-8"))
    source_lines = (BACKEND / "rule_sources.txt").read_text(encoding="utf-8").splitlines()[5:]
    source_pairs = {(parts[0], parts[1]) for line in source_lines
                    if (parts := [part.strip() for part in line.split(" | ")])}
    record_pairs = {(row["region"], row["material"]) for row in records}
    assert len(records) == len(record_pairs) == len(source_pairs) == 120
    assert record_pairs == source_pairs
    assert len({row["region"] for row in records}) == 10
    assert len({row["instructions"] for row in records}) <= 25
    assert all(row["category"] in {"recyclable", "compostable", "landfill"} for row in records)
    hagen_bio = next(row for row in records if row["region"] == "Hagen" and row["material"] == "biological")
    munich_plastic = next(row for row in records if row["region"] == "München" and row["material"] == "plastic")
    assert "recycling centre" in hagen_bio["instructions"]
    assert "Wertstoffinsel" in munich_plastic["instructions"]


def test_fallback_client_uses_teammates_multipart_contract(monkeypatch):
    observed = {}

    def fake_post(url, *, files, data, timeout):
        observed.update(url=url, files=files, data=data, timeout=timeout)
        class Response:
            def raise_for_status(self):
                pass
            def json(self):
                return {"category": "recyclable", "material": "battery", "instructions": "AI text"}
        return Response()

    monkeypatch.setattr("httpx.post", fake_post)
    result = AssistantFallbackClient("http://localhost:8000").classify(
        PHOTO, "image/jpeg", "Dortmund", ["battery", "paper"]
    )
    assert observed["url"] == "http://localhost:8000/fallback/classify"
    assert observed["files"]["image"][1:] == (PHOTO, "image/jpeg")
    assert observed["data"]["region"] == "Dortmund"
    assert json.loads(observed["data"]["materials"]) == ["battery", "paper"]
    assert result.material == "battery"
    assert not hasattr(result, "instructions")
    assert not hasattr(result, "category")


def test_fallback_rejects_material_outside_region_list(monkeypatch):
    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"material": "unlisted"}

    monkeypatch.setattr("httpx.post", lambda *args, **kwargs: Response())
    result = AssistantFallbackClient("http://localhost:8000").classify(
        PHOTO, "image/jpeg", "Dortmund", ["battery"]
    )
    assert result.material is None


def test_analytics_client_sends_dashboard_schema(monkeypatch):
    observed = {}

    class Response:
        def raise_for_status(self):
            pass

    def fake_post(url, *, json, headers, timeout):
        observed.update(url=url, json=json, headers=headers, timeout=timeout)
        return Response()

    monkeypatch.setattr("httpx.post", fake_post)
    assert AnalyticsClient("http://localhost:8001", "test-key").record(
        "battery", "recyclable", "Dortmund"
    )
    assert observed["url"] == "http://localhost:8001/analytics/records"
    assert observed["json"] == {
        "item": "battery", "category": "recyclable", "region_code": "Dortmund"
    }
    assert observed["headers"] == {"X-Analytics-Key": "test-key"}


def test_fallback_service_failure_requests_new_photo(make_engine, monkeypatch):
    import httpx

    def offline(*args, **kwargs):
        raise httpx.ConnectError("offline")

    monkeypatch.setattr("httpx.post", offline)
    fallback = AssistantFallbackClient("http://localhost:8000")
    outcome = make_engine(FakeClassifier(confidence=0.1), fallback).get_recommendation(
        ImageQuery(PHOTO, "Dortmund")
    )
    assert outcome.status == "retry_photo"


def test_image_contents_must_match_declared_type(make_engine):
    from io import BytesIO
    from PIL import Image

    buffer = BytesIO()
    Image.new("RGB", (20, 20), "red").save(buffer, format="PNG")
    with pytest.raises(InvalidImageError, match="MIME type"):
        make_engine().get_recommendation(ImageQuery(buffer.getvalue(), "Dortmund", "image/jpeg"))


def test_class_mapping_can_change_without_reloading_cv_model(make_engine, tmp_path):
    mapping_path = tmp_path / "mapping.json"
    mapping_path.write_text((BACKEND / "class_mapping.json").read_text(encoding="utf-8"), encoding="utf-8")
    engine = make_engine()
    engine.mapping = ClassMapping(mapping_path)
    payload = json.loads(mapping_path.read_text(encoding="utf-8"))
    payload["model_classes"]["battery"] = "paper"
    mapping_path.write_text(json.dumps(payload), encoding="utf-8")
    engine.mapping.reload()
    outcome = engine.get_recommendation(ImageQuery(PHOTO, "Dortmund"))
    assert outcome.classification.waste_class == "paper"
    assert outcome.category == "recyclable"
    assert "paper bin" in outcome.message


def test_each_region_offers_every_model_material(rules):
    mapping = ClassMapping(BACKEND / "class_mapping.json")
    for region in rules.list_regions():
        assert set(rules.list_materials(region)) == set(mapping.model_classes.values())


def test_api_validates_upload_and_returns_result(make_engine):
    photo = UploadFile(file=BytesIO(PHOTO), filename="battery.jpg",
                       headers=Headers({"content-type": "image/jpeg"}))
    result = recommend(photo, "Dortmund", make_engine())
    assert result["classification"]["waste_class"] == "battery"

    invalid = UploadFile(file=BytesIO(PHOTO), filename="bad.gif",
                         headers=Headers({"content-type": "image/gif"}))
    with pytest.raises(HTTPException) as exc:
        recommend(invalid, "Dortmund", make_engine())
    assert exc.value.status_code == 400


def test_real_model_recognizes_battery():
    image = ImageProcessor().prepare(PHOTO, "image/jpeg")
    result = WasteClassifier(BACKEND / "model" / "resnet50_garbage_classificationv1.2.pth").classify(image)
    assert result.waste_class == "battery"
    assert result.confidence > 0.8


def test_conveyor_pipeline_filters_and_routes_events():
    events = [
        PredictionEvent("low", "plastic", 0.4, (0, 0, 100, 100), ("PET",)),
        PredictionEvent("pet", "plastic", 0.9, (0, 0, 200, 200), ("PET",)),
        PredictionEvent("metal", "metal", 0.95, (0, 0, 40, 40), ("aluminum",)),
    ]
    stream = PredictionStream(events, ConfidenceFilter(0.8) | MaterialRouter())
    results = list(stream.routed())
    assert [(x.image_id, x.material, x.routing_code) for x in results] == [
        ("pet", "PET", "PET_LARGE"), ("metal", "ALUMINUM", "ALUMINUM_SMALL")
    ]


def test_conveyor_pipeline_drops_missing_material_and_invalid_box():
    events = [
        PredictionEvent("unknown", "plastic", 0.9, (0, 0, 50, 50), ("other",)),
        PredictionEvent("empty", "plastic", 0.9, (2, 2, 2, 2), ("HDPE",)),
    ]
    assert list(PredictionStream(events, ConfidenceFilter() | MaterialRouter())) == []
