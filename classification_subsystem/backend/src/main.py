"""Web API for waste classification and disposal recommendations."""

from functools import lru_cache
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile

from .analytics_client import AnalyticsClient
from .class_mapping import ClassMapping
from .db_config import get_rules_db_url, get_setting
from .engine import DisposalRecommendationEngine
from .errors import ClassificationError
from .fallback_client import AssistantFallbackClient
from .image_processing import ImageProcessor
from .models import ImageQuery
from .regional_rules import RegionalRulesService
from .wasteclassifier import WasteClassifier


BACKEND_DIR = Path(__file__).resolve().parents[1]


@lru_cache
def get_rules_service() -> RegionalRulesService:
    return RegionalRulesService(get_rules_db_url())


@lru_cache
def get_engine() -> DisposalRecommendationEngine:
    fallback_url = get_setting("ASSISTANT_FALLBACK_URL")
    analytics_url = get_setting("ANALYTICS_URL")
    analytics_key = get_setting("ANALYTICS_INGEST_KEY")

    fallback = AssistantFallbackClient(fallback_url) if fallback_url else None
    statistics = (
        AnalyticsClient(analytics_url, analytics_key)
        if analytics_url and analytics_key else None
    )
    return DisposalRecommendationEngine(
        WasteClassifier(BACKEND_DIR / "model" / "resnet50_garbage_classificationv1.2.pth"),
        get_rules_service(),
        ClassMapping(BACKEND_DIR / "class_mapping.json"),
        ImageProcessor(),
        fallback=fallback,
        statistics=statistics,
    )


app = FastAPI(title="Waste Classification and Sorting")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/classification/regions")
def regions(rules: RegionalRulesService = Depends(get_rules_service)):
    return {"regions": rules.list_regions()}


@app.post("/classification/recommend")
def recommend(
    image: UploadFile = File(...),
    region: str = Form(...),
    engine: DisposalRecommendationEngine = Depends(get_engine),
):
    try:
        query = ImageQuery(image.file.read(), region, image.content_type or "image/jpeg")
        result = engine.get_recommendation(query)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ClassificationError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

    classification = result.classification
    return {
        "status": result.get_status(),
        "region": result.region,
        "message": result.message,
        "category": result.category.value,
        "classification": None if classification is None else {
            "waste_class": classification.waste_class,
            "confidence": classification.get_confidence(),
            "source": classification.source,
        },
    }
