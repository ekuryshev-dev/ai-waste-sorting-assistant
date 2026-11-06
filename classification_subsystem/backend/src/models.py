from enum import Enum

from sqlmodel import Field, SQLModel


class Category(str, Enum):
    unknown = "unknown"
    recyclable = "recyclable"
    compostable = "compostable"
    landfill = "landfill"


class ImageQuery:
    def __init__(self, image: bytes, region: str, mime_type: str = "image/jpeg"):
        self.image = image
        self.set_region(region)
        self.mime_type = mime_type

    def get_region(self) -> str:
        return self._region

    def set_region(self, value: str) -> None:
        self._region = value


class ClassificationResult:
    def __init__(self, waste_class: str | None, confidence: float | None,
                 source: str = "cv"):
        self.waste_class = waste_class
        self.set_confidence(confidence)
        self.source = source

    def get_confidence(self) -> float | None:
        return self._confidence

    def set_confidence(self, value: float | None) -> None:
        self._confidence = value


class DisposalRecommendation:
    def __init__(
        self,
        status: str,
        region: str,
        message: str,
        classification: ClassificationResult | None = None,
        category: Category = Category.unknown,
    ):
        self.set_status(status)
        self.region = region
        self.message = message
        self.classification = classification
        self.category = category

    def get_status(self) -> str:
        return self._status

    def set_status(self, value: str) -> None:
        self._status = value


class RecyclingRule(SQLModel, table=True):
    __tablename__ = "classification_recycling_rules"

    id: int | None = Field(default=None, primary_key=True)
    region: str = Field(index=True)
    material: str
    category: Category
    instructions: str | None = None


class FallbackResult:
    def __init__(self, category: Category = Category.unknown,
                 material: str | None = None, instructions: str | None = None):
        self.category = category
        self.material = material
        self.instructions = instructions
