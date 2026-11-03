from dataclasses import dataclass
from enum import Enum
from typing import Literal

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


@dataclass(frozen=True)
class ImageQuery:
    image: bytes
    region: str
    mime_type: str = "image/jpeg"


@dataclass(frozen=True)
class ClassificationResult:
    waste_class: str
    confidence: float | None
    source: Literal["cv", "ai"]


@dataclass(frozen=True)
class DisposalRecommendation:
    status: Literal["ok", "retry_photo"]
    region: str
    message: str
    classification: ClassificationResult | None = None
    category: str = "unknown"


class Category(str, Enum):
    unknown = "unknown"
    recyclable = "recyclable"
    compostable = "compostable"
    landfill = "landfill"


class RecyclingRule(SQLModel, table=True):
    __tablename__ = "classification_recycling_rules"
    __table_args__ = (
        UniqueConstraint("region", "material", name="uq_classification_region_material"),
    )

    id: int | None = Field(default=None, primary_key=True)
    region: str = Field(index=True)
    material: str
    category: Category
    instructions: str | None = None


@dataclass(frozen=True)
class FallbackResult:
    material: str | None
