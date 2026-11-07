from io import BytesIO
from pathlib import Path

import pytest
from fastapi import HTTPException, UploadFile
from sqlmodel import Session, SQLModel
from starlette.datastructures import Headers

from classification_subsystem.backend.src.class_mapping import ClassMapping
from classification_subsystem.backend.src.engine import DisposalRecommendationEngine
from classification_subsystem.backend.src.errors import ClassificationError
from classification_subsystem.backend.src.image_processing import ImageProcessor
from classification_subsystem.backend.src.main import recommend
from classification_subsystem.backend.src.models import (
    Category, ClassificationResult, FallbackResult, ImageQuery, RecyclingRule,
)
from classification_subsystem.backend.src.regional_rules import RegionalRulesService
from classification_subsystem.backend.src.stream_processing import ConfidenceFilter, PredictionEvent


BACKEND = Path(__file__).resolve().parents[1]
PHOTO = (BACKEND / "examples" / "battery1.jpg").read_bytes()


class FakeClassifier:
    def __init__(self, label="battery", confidence=0.9):
        self.label = label
        self.confidence = confidence

    def classify(self, image):
        return ClassificationResult(self.label, self.confidence)


class FakeFallback:
    def __init__(self, result):
        self.result = result

    def classify(self, image, mime_type, region):
        return self.result


class FakeStatistics:
    def __init__(self):
        self.records = []

    def record(self, material, category, region):
        self.records.append((material, category, region))


def make_rules(tmp_path):
    rules = RegionalRulesService(f"sqlite:///{tmp_path / 'rules.db'}")
    SQLModel.metadata.create_all(rules.engine)
    with Session(rules.engine) as session:
        session.add(RecyclingRule(
            region="Dortmund", material="battery", category=Category.recyclable,
            instructions="Take batteries to a collection point.",
        ))
        session.commit()
    return rules


def make_engine(tmp_path, classifier=None, fallback=None, statistics=None):
    return DisposalRecommendationEngine(
        classifier or FakeClassifier(),
        make_rules(tmp_path),
        ClassMapping(BACKEND / "class_mapping.json"),
        ImageProcessor(),
        fallback=fallback,
        statistics=statistics,
    )


def upload(data):
    return UploadFile(
        file=BytesIO(data), filename="photo.jpg",
        headers=Headers({"content-type": "image/jpeg"}),
    )


def test_image_processor_prepares_photo():
    image = ImageProcessor().prepare(PHOTO)
    assert image.size == (224, 224)
    assert image.mode == "RGB"


def test_invalid_image_raises_classification_error():
    with pytest.raises(ClassificationError, match="not a valid image"):
        ImageProcessor().prepare(b"not an image")


def test_class_mapping_translates_model_label():
    mapping = ClassMapping(BACKEND / "class_mapping.json")
    assert mapping.from_model("battery") == "battery"
    assert mapping.from_model("unlisted") is None


def test_regional_rule_returns_category_and_instructions(tmp_path):
    category, instructions = make_rules(tmp_path).get_rule("battery", "Dortmund")
    assert category == Category.recyclable
    assert "collection point" in instructions


def test_missing_regional_rule_raises_classification_error(tmp_path):
    with pytest.raises(ClassificationError) as error:
        make_rules(tmp_path).get_rule("metal", "Dortmund")
    assert error.value.status_code == 422


def test_confidence_threshold_must_be_between_zero_and_one(tmp_path):
    engine = make_engine(tmp_path)
    with pytest.raises(ValueError):
        engine.set_confidence_threshold(-0.1)


def test_confident_prediction_uses_regional_rule_and_analytics(tmp_path):
    statistics = FakeStatistics()
    result = make_engine(tmp_path, statistics=statistics).get_recommendation(
        ImageQuery(PHOTO, "Dortmund")
    )
    assert result.get_status() == "ok"
    assert result.classification.waste_class == "battery"
    assert result.classification.source == "cv"
    assert result.message == "Take batteries to a collection point."
    assert statistics.records == [("battery", "recyclable", "Dortmund")]


def test_uncertain_prediction_uses_ai_instructions_without_analytics(tmp_path):
    statistics = FakeStatistics()
    fallback = FakeFallback(FallbackResult(Category.recyclable, "battery", "AI advice"))
    result = make_engine(
        tmp_path, FakeClassifier(confidence=0.2), fallback, statistics
    ).get_recommendation(ImageQuery(PHOTO, "Dortmund"))
    assert result.get_status() == "ok"
    assert result.message == "AI advice"
    assert result.classification.source == "ai"
    assert statistics.records == []


def test_ai_without_instructions_requests_another_photo(tmp_path):
    fallback = FakeFallback(FallbackResult(Category.recyclable, "battery"))
    result = make_engine(
        tmp_path, FakeClassifier(confidence=0.2), fallback
    ).get_recommendation(ImageQuery(PHOTO, "Dortmund"))
    assert result.get_status() == "retry_photo"


def test_uncertain_prediction_without_ai_requests_another_photo(tmp_path):
    result = make_engine(
        tmp_path, FakeClassifier(confidence=0.2)
    ).get_recommendation(ImageQuery(PHOTO, "Dortmund"))
    assert result.get_status() == "retry_photo"


def test_unsupported_region_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="Unsupported region"):
        make_engine(tmp_path).get_recommendation(ImageQuery(PHOTO, "Unknown"))


def test_confidence_filter_drops_low_predictions():
    low = PredictionEvent("1.jpg", "battery", 0.5, 0.7)
    high = PredictionEvent("2.jpg", "battery", 0.9, 0.7)
    filter_step = ConfidenceFilter()
    assert filter_step.process(low) is None
    assert filter_step.process(high) is high


def test_api_returns_a_recommendation(tmp_path):
    result = recommend(upload(PHOTO), "Dortmund", make_engine(tmp_path))
    assert result["status"] == "ok"
    assert result["classification"]["waste_class"] == "battery"


def test_api_rejects_invalid_image_with_400(tmp_path):
    with pytest.raises(HTTPException) as error:
        recommend(upload(b"not an image"), "Dortmund", make_engine(tmp_path))
    assert error.value.status_code == 400


def test_api_reports_missing_rule_with_422(tmp_path):
    with pytest.raises(HTTPException) as error:
        recommend(upload(PHOTO), "Dortmund", make_engine(tmp_path, FakeClassifier("metal")))
    assert error.value.status_code == 422
