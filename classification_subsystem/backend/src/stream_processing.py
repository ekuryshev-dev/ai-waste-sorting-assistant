"""Process example images as a stream of classification events."""

import json
from abc import ABC, abstractmethod
from pathlib import Path

from .image_processing import ImageProcessor
from .wasteclassifier import WasteClassifier


class PredictionEvent:
    def __init__(self, image_id: str, waste_class: str, confidence: float,
                 threshold: float):
        self.image_id = image_id
        self.waste_class = waste_class
        self.confidence = confidence
        self.above_threshold = confidence >= threshold


class StreamProcessor(ABC):
    @abstractmethod
    def process(self, value):
        pass

    def __or__(self, other):
        return Pipeline([self, other])


class ImageClassifierProcessor(StreamProcessor):
    def __init__(self, classifier: WasteClassifier,
                 image_processor: ImageProcessor, threshold: float):
        self.classifier = classifier
        self.image_processor = image_processor
        self.threshold = threshold

    def process(self, image_path: Path) -> PredictionEvent:
        image = self.image_processor.prepare(image_path.read_bytes())
        result = self.classifier.classify(image)
        return PredictionEvent(image_path.name, result.waste_class,
                               result.get_confidence(), self.threshold)


class JsonlWriter(StreamProcessor):
    def __init__(self, path: Path):
        self.path = path
        self.count = 0

    def process(self, event: PredictionEvent) -> PredictionEvent:
        row = {
            "image_id": event.image_id,
            "class": event.waste_class,
            "confidence": event.confidence,
            "above_threshold": event.above_threshold,
        }
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row) + "\n")
        self.count += 1
        return event


class ConfidenceFilter(StreamProcessor):
    def process(self, event: PredictionEvent) -> PredictionEvent | None:
        if event.above_threshold:
            return event
        return None


class Pipeline(StreamProcessor):
    def __init__(self, processors: list[StreamProcessor]):
        self.processors = processors

    def __or__(self, other):
        return Pipeline(self.processors + [other])

    def process(self, value):
        current = value
        for processor in self.processors:
            current = processor.process(current)
            if current is None:
                return None
        return current


class PredictionStream:
    def __init__(self, image_paths, pipeline: Pipeline):
        self.images = iter(image_paths)
        self.pipeline = pipeline

    def __iter__(self):
        return self

    def __next__(self) -> PredictionEvent:
        while True:
            image_path = next(self.images)
            event = self.pipeline.process(image_path)
            if event is not None:
                return event


def image_paths(directory: Path):
    """Yield image paths one at a time; image bytes are read later."""
    for path in sorted(directory.iterdir()):
        if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            yield path
