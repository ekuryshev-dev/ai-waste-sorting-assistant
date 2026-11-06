from .class_mapping import ClassMapping
from .image_processing import ImageProcessor
from .models import Category, ClassificationResult, DisposalRecommendation, ImageQuery
from .regional_rules import RegionalRulesService
from .wasteclassifier import WasteClassifier


class DisposalRecommendationEngine:
    """Classify an image and return a disposal recommendation."""

    def __init__(
        self,
        classifier: WasteClassifier,
        rules_service: RegionalRulesService,
        mapping: ClassMapping,
        image_processor: ImageProcessor,
        fallback=None,
        statistics=None,
        confidence_threshold: float = 0.7,
    ):
        self.classifier = classifier
        self.rules_service = rules_service
        self.mapping = mapping
        self.image_processor = image_processor
        self.fallback = fallback
        self.statistics = statistics
        self.set_confidence_threshold(confidence_threshold)

    def get_confidence_threshold(self) -> float:
        return self._confidence_threshold

    def set_confidence_threshold(self, value: float) -> None:
        if not 0 <= value <= 1:
            raise ValueError("confidence_threshold must be between 0 and 1")
        self._confidence_threshold = value

    def get_recommendation(self, query: ImageQuery) -> DisposalRecommendation:
        region = query.get_region()
        if region not in self.rules_service.list_regions():
            raise ValueError(f"Unsupported region: {region}")

        image = self.image_processor.prepare(query.image)
        cv_result = self.classifier.classify(image)
        material = self.mapping.from_model(cv_result.waste_class)

        if cv_result.get_confidence() >= self.get_confidence_threshold() and material:
            category, instructions = self.rules_service.get_rule(material, region)
            classification = ClassificationResult(material, cv_result.get_confidence(), "cv")
            if self.statistics is not None:
                self.statistics.record(material, category.value, region)
            return DisposalRecommendation("ok", region, instructions, classification, category)

        if self.fallback is not None:
            ai_result = self.fallback.classify(query.image, query.mime_type, region)
            if ai_result.category != Category.unknown and ai_result.instructions:
                classification = ClassificationResult(ai_result.material, None, "ai")
                return DisposalRecommendation(
                    "ok", region, ai_result.instructions, classification, ai_result.category
                )

        return DisposalRecommendation(
            "retry_photo", region,
            "We could not identify the item. Please upload another photo.",
        )
