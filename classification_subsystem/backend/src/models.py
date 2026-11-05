from enum import Enum


class Category(str, Enum):
    unknown = "unknown"
    recyclable = "recyclable"
    compostable = "compostable"
    landfill = "landfill"


class ImageQuery:
    def __init__(self, image: bytes, region: str):
        self.image = image
        self.set_region(region)

    def get_region(self) -> str:
        return self._region

    def set_region(self, value: str) -> None:
        self._region = value


class ClassificationResult:
    def __init__(self, waste_class: str, confidence: float):
        self.waste_class = waste_class
        self.set_confidence(confidence)

    def get_confidence(self) -> float:
        return self._confidence

    def set_confidence(self, value: float) -> None:
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
