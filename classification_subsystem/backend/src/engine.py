from .class_mapping import ClassMapping
from .errors import RuleNotFoundError
from .image_processing import ImageProcessor
from .models import ClassificationResult, DisposalRecommendation, ImageQuery
from .regional_rules import RegionalRulesService
from .wasteclassifier import WasteClassifier


class DisposalRecommendationEngine:
    def __init__(
        self,
        classifier: WasteClassifier,
        rules_service: RegionalRulesService,
        mapping: ClassMapping,
        image_processor: ImageProcessor,
        fallback=None,
        statistics=None,
        confidence_threshold: float = 0.8,
    ):
        self.classifier = classifier
        self.rules_service = rules_service
        self.mapping = mapping
        self.image_processor = image_processor
        self.fallback = fallback
        self.statistics = statistics
        self.confidence_threshold = confidence_threshold

    @property
    def confidence_threshold(self) -> float:
        return self._confidence_threshold

    @confidence_threshold.setter
    def confidence_threshold(self, value: float) -> None:
        if not 0.0 <= value <= 1.0:
            raise ValueError("confidence_threshold must be between 0 and 1")
        self._confidence_threshold = value

    def get_recommendation(self, query: ImageQuery) -> DisposalRecommendation:
        if query.region not in self.rules_service.list_regions():
            raise ValueError(f"Unsupported region: {query.region}")

        prepared = self.image_processor.prepare(query.image, query.mime_type)
        cv_result = self.classifier.classify(prepared)
        waste_class = self.mapping.from_model(cv_result.waste_class)
        result = None

        if cv_result.confidence is not None and cv_result.confidence >= self.confidence_threshold and waste_class:
            result = ClassificationResult(waste_class, cv_result.confidence, "cv")
        elif self.fallback is not None:
            allowed_materials = self.rules_service.list_materials(query.region)
            ai_result = self.fallback.classify(
                query.image, query.mime_type, query.region, allowed_materials
            )
            if ai_result.material in allowed_materials:
                result = ClassificationResult(ai_result.material, None, "ai")

        if result is None:
            return DisposalRecommendation(
                "retry_photo", query.region,
                "We could not identify the item. Please upload another photo.",
            )

        rule = self.rules_service.get_rule(result.waste_class, query.region)
        if not rule.instructions:
            raise RuleNotFoundError("Regional rule has no disposal instructions")
        if self.statistics is not None:
            self.statistics.record(result.waste_class, rule.category.value, query.region)
        return DisposalRecommendation("ok", query.region, rule.instructions, result, rule.category.value)
