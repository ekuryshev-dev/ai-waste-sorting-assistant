from .class_mapping import ClassMapping
from .image_processing import ImageProcessor
from .models import DisposalRecommendation, ImageQuery
from .regional_rules import RegionalRulesService
from .wasteclassifier import WasteClassifier


class DisposalRecommendationEngine:
    """Connect image preparation, CV classification and regional rules."""

    def __init__(
        self,
        classifier: WasteClassifier,
        rules_service: RegionalRulesService,
        mapping: ClassMapping,
        image_processor: ImageProcessor,
        confidence_threshold: float = 0.7,
    ):
        self.classifier = classifier
        self.rules_service = rules_service
        self.mapping = mapping
        self.image_processor = image_processor
        self.set_confidence_threshold(confidence_threshold)

    def get_confidence_threshold(self) -> float:
        return self._confidence_threshold

    def set_confidence_threshold(self, value: float) -> None:
        if not 0 <= value <= 1:
            raise ValueError("confidence_threshold must be between 0 and 1")
        self._confidence_threshold = value

    def get_recommendation(self, query: ImageQuery) -> DisposalRecommendation:
        if query.get_region() not in self.rules_service.list_regions():
            raise ValueError(f"Unsupported region: {query.get_region()}")

        image = self.image_processor.prepare(query.image)
        classification = self.classifier.classify(image)
        material = self.mapping.from_model(classification.waste_class)
        if classification.get_confidence() < self.get_confidence_threshold() or material is None:
            return DisposalRecommendation(
                "retry_photo", query.get_region(),
                "We could not identify the item. Please upload another photo.",
            )

        category, instructions = self.rules_service.get_rule(material, query.get_region())
        classification.waste_class = material
        return DisposalRecommendation("ok", query.get_region(), instructions, classification, category)
