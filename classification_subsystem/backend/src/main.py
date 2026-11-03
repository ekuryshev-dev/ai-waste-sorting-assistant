import os
from contextlib import asynccontextmanager
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile

from .analytics_client import AnalyticsClient
from .class_mapping import ClassMapping
from .db_config import get_rules_db_url
from .engine import DisposalRecommendationEngine
from .errors import InvalidImageError, RuleNotFoundError
from .fallback_client import AssistantFallbackClient
from .image_processing import ImageProcessor
from .models import ImageQuery
from .regional_rules import RegionalRulesService
from .wasteclassifier import WasteClassifier


BACKEND_DIR = Path(__file__).resolve().parents[1]


@lru_cache
def get_engine() -> DisposalRecommendationEngine:
    model_path = Path(os.getenv(
        "WASTE_MODEL_PATH", str(BACKEND_DIR / "model" / "resnet50_garbage_classificationv1.2.pth")
    ))
    rules = RegionalRulesService(get_rules_db_url())
    fallback_url = os.getenv("ASSISTANT_FALLBACK_URL")
    fallback = AssistantFallbackClient(fallback_url) if fallback_url else None
    analytics_url = os.getenv("ANALYTICS_URL")
    analytics_key = os.getenv("ANALYTICS_INGEST_KEY")
    statistics = AnalyticsClient(analytics_url, analytics_key) if analytics_url and analytics_key else None
    return DisposalRecommendationEngine(
        WasteClassifier(model_path), rules, ClassMapping(BACKEND_DIR / "class_mapping.json"),
        ImageProcessor(), fallback=fallback, statistics=statistics,
        confidence_threshold=float(os.getenv("CV_CONFIDENCE_THRESHOLD", "0.8")),
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_engine()  # Load the CV model before the first request.
    yield


app = FastAPI(title="Waste Classification and Sorting", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/classification/regions")
def regions(engine: DisposalRecommendationEngine = Depends(get_engine)):
    return {"regions": engine.rules_service.list_regions()}


@app.post("/classification/recommend")
def recommend(
    image: UploadFile = File(...),
    region: str = Form(...),
    engine: DisposalRecommendationEngine = Depends(get_engine),
):
    data = image.file.read(engine.image_processor.max_bytes + 1)
    try:
        result = engine.get_recommendation(ImageQuery(data, region, image.content_type or ""))
    except InvalidImageError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuleNotFoundError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return asdict(result)
