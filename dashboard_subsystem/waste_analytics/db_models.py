
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field


class WasteRecordRow(SQLModel, table=True):
    __tablename__ = "analytics_waste_records"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    item: str
    category: str
    region_code: str = Field(index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
