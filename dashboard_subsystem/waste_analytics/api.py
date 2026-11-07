
import os
import secrets
from contextlib import asynccontextmanager

from datetime import datetime, timedelta, timezone

from fastapi import Query
from fastapi import FastAPI, Header, HTTPException
from fastapi import Request
from fastapi import WebSocket, WebSocketDisconnect

from pydantic import BaseModel
from sqlmodel import SQLModel

from starlette.concurrency import run_in_threadpool

from waste_analytics.category import Category
from waste_analytics.database import engine
from waste_analytics.db_models import WasteRecordRow
from waste_analytics.waste_record import WasteRecord
from waste_analytics.sql_waste_repository import SQLWasteRepository
from waste_analytics.waste_analytics_service import WasteAnalyticsService
from waste_analytics.analytics_controller import AnalyticsController
from waste_analytics.error_handler import WasteAnalyticsError
from waste_analytics.error_handler import WasteAnalyticsErrorHandler
from waste_analytics.validation_processor import ValidationProcessor
from waste_analytics.analytics_processor import AnalyticsProcessor
from waste_analytics.websocket_manager import AnalyticsConnectionManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(
        engine,
        tables=[WasteRecordRow.__table__]
    )
    yield


app = FastAPI(title="Waste Analytics API", lifespan=lifespan)

WasteAnalyticsErrorHandler.register(app)

repository = SQLWasteRepository(engine)
service = WasteAnalyticsService(repository)
controller = AnalyticsController(service)

pipeline = ValidationProcessor() | AnalyticsProcessor(repository)

#This is a place within a FastAPI application where store objects that are needed by various API functions.
app.state.repository = repository #Working with databases
app.state.controller = controller #Statistics
app.state.pipeline = pipeline #Processing records
app.state.ws_manager = AnalyticsConnectionManager() #WebSocket-clients

class NewRecord(BaseModel):
    item: str
    category: Category
    region_code: str


def get_filtered_records(region_code, days=None):
    if region_code == "__all__":
        records = repository.get_all()
    else:
        records = service.get_records_by_region(region_code)
    if days is None:
        return records

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    filtered = []

    for record in records:
        created_at = record.get_created_at()

        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        if created_at >= cutoff:
            filtered.append(record)

    return filtered

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analytics/records", status_code=201)
async def add_record(
    data: NewRecord,
    request: Request,
    x_analytics_key: str | None = Header(default=None)
):
    expected_key = os.getenv("ANALYTICS_INGEST_KEY")

    if (
        not expected_key
        or not x_analytics_key
        or not secrets.compare_digest(x_analytics_key, expected_key)
    ):
        raise HTTPException(status_code=403, detail="Forbidden")

    if not data.item.strip():
        raise WasteAnalyticsError(
            "Item name cannot be empty",
            400
        )

    if not data.region_code.strip():
        raise WasteAnalyticsError(
            "Region code cannot be empty",
            400
        )

    record = WasteRecord(
        data.item,
        data.category,
        data.region_code
    )

    try:
        await run_in_threadpool(
            request.app.state.pipeline.process,
            record
        )
    except (ValueError, TypeError) as exc:
        raise WasteAnalyticsError(str(exc), 400) from exc

    await request.app.state.ws_manager.broadcast_update(
        record.get_region_code()
    )

    return {
        "id": str(record.get_id()),
        "status": "saved"
    }


@app.get("/analytics/regions")
def get_regions(request: Request):
    regions = request.app.state.repository.get_regions()
    return {"regions": regions}

@app.get("/analytics/{region_code}/statistics")
def get_statistics(
    region_code: str,
    days: int | None = Query(default=None, ge=1)
):
    records = get_filtered_records(region_code, days)
    summary = service.calculate_statistics(records)
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
def get_trends(
    region_code: str,
    days: int | None = Query(default=None, ge=1)
):
    records = get_filtered_records(region_code, days)
    trends = service.calculate_trends(records)

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


@app.websocket("/analytics/ws")
async def analytics_websocket(websocket: WebSocket):

    manager = websocket.app.state.ws_manager #get manager from app.state

    await manager.connect(websocket) #Accepts a connection and saves it

    try:
        while True: #Maintains the connection while waiting for a message
            await websocket.receive_text() #Waits for data and allows for the detection of a disconnection

    except WebSocketDisconnect: #Handles connection closure
        pass

    finally: #Removes a disconnected client from the list
        manager.disconnect(websocket)

