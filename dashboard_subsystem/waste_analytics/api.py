
import os
import secrets
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from sqlmodel import SQLModel

from waste_analytics.category import Category
from waste_analytics.database import engine
from waste_analytics.db_models import WasteRecordRow
from waste_analytics.waste_record import WasteRecord
from waste_analytics.sql_waste_repository import SQLWasteRepository
from waste_analytics.waste_analytics_service import WasteAnalyticsService
from waste_analytics.analytics_controller import AnalyticsController


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(
        engine,
        tables=[WasteRecordRow.__table__]
    )
    yield


app = FastAPI(title="Waste Analytics API", lifespan=lifespan)

repository = SQLWasteRepository(engine)
service = WasteAnalyticsService(repository)
controller = AnalyticsController(service)


class NewRecord(BaseModel):
    item: str
    category: Category
    region_code: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analytics/records", status_code=201)
def add_record(
    data: NewRecord,
    x_analytics_key: str | None = Header(default=None)
):
    expected_key = os.getenv("ANALYTICS_INGEST_KEY")

    if (
        not expected_key
        or not x_analytics_key
        or not secrets.compare_digest(x_analytics_key, expected_key)
    ):
        raise HTTPException(status_code=403, detail="Forbidden")

    record = WasteRecord(
        data.item,
        data.category,
        data.region_code
    )

    repository.add(record)

    return {"id": str(record.get_id()), "status": "saved"}


@app.get("/analytics/{region_code}/statistics")
def get_statistics(region_code: str):
    summary = controller.get_statistics(region_code)
    records = service.get_records_by_region(region_code)
    counts = service.calculate_category_distribution(records)

    total = summary.get_total_records()

    unknown_percentage = 0.0
    if total > 0:
        unknown_percentage = counts[Category.unknown] / total * 100

    return {
        "region": region_code,
        "total_records": total,
        "recyclable_percentage": summary.get_recyclable_percentage(),
        "compostable_percentage": summary.get_compostable_percentage(),
        "landfill_percentage": summary.get_landfill_percentage(),
        "unknown_percentage": unknown_percentage,
        "recyclable_share": summary.get_recycling_rate()
    }


@app.get("/analytics/{region_code}/trends")
def get_trends(region_code: str):
    trends = controller.get_trends(region_code)

    result = []

    for point in trends:
        result.append({
            "period": point.get_period(),
            "recyclable_count": point.get_recyclable_count(),
            "compostable_count": point.get_compostable_count(),
            "landfill_count": point.get_landfill_count(),
            "unknown_count": point.get_unknown_count()
        })

    return result
