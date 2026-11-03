"""Independent Hometask 2 example for conveyor-belt classification events."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Iterator


@dataclass(frozen=True)
class PredictionEvent:
    image_id: str
    model_label: str
    confidence: float
    bbox: tuple[int, int, int, int]  # left, top, right, bottom
    visual_tags: tuple[str, ...]


@dataclass(frozen=True)
class RoutedEvent:
    image_id: str
    material: str
    routing_code: str
    bbox_area: int
    confidence: float


class StreamProcessor(ABC):
    @abstractmethod
    def process(self, event: PredictionEvent | RoutedEvent):
        """Return a transformed event or None to drop it."""

    def __or__(self, other: "StreamProcessor") -> "Pipeline":
        if not isinstance(other, StreamProcessor):
            return NotImplemented
        return Pipeline([self, other])


class ConfidenceFilter(StreamProcessor):
    def __init__(self, threshold: float = 0.8):
        self.threshold = threshold

    @property
    def threshold(self) -> float:
        return self._threshold

    @threshold.setter
    def threshold(self, value: float) -> None:
        if not 0 <= value <= 1:
            raise ValueError("threshold must be between 0 and 1")
        self._threshold = value

    def process(self, event: PredictionEvent) -> PredictionEvent | None:
        return event if event.confidence >= self.threshold else None


class MaterialRouter(StreamProcessor):
    MATERIALS = {"PET": "PET", "HDPE": "HDPE", "ALUMINUM": "ALUMINUM"}

    def __init__(self, large_area: int = 20_000):
        self.large_area = large_area

    @property
    def large_area(self) -> int:
        return self._large_area

    @large_area.setter
    def large_area(self, value: int) -> None:
        if value <= 0:
            raise ValueError("large_area must be positive")
        self._large_area = value

    def process(self, event: PredictionEvent) -> RoutedEvent | None:
        left, top, right, bottom = event.bbox
        area = max(0, right - left) * max(0, bottom - top)
        if area == 0:
            return None
        tags = {tag.upper() for tag in event.visual_tags}
        material = next((name for name in self.MATERIALS if name in tags), None)
        if material is None:
            return None
        size = "LARGE" if area >= self.large_area else "SMALL"
        return RoutedEvent(event.image_id, material, f"{material}_{size}", area, event.confidence)


class Pipeline(StreamProcessor):
    def __init__(self, processors: list[StreamProcessor]):
        self.processors = processors

    def __or__(self, other: StreamProcessor) -> "Pipeline":
        if not isinstance(other, StreamProcessor):
            return NotImplemented
        return Pipeline([*self.processors, other])

    def process(self, event: PredictionEvent):
        current = event
        for processor in self.processors:
            current = processor.process(current)
            if current is None:
                return None
        return current


class PredictionStream(Iterator[RoutedEvent]):
    def __init__(self, events: Iterable[PredictionEvent], pipeline: Pipeline):
        self._events = iter(events)
        self.pipeline = pipeline

    def __iter__(self) -> "PredictionStream":
        return self

    def __next__(self) -> RoutedEvent:
        while True:
            event = next(self._events)
            result = self.pipeline.process(event)
            if result is not None:
                return result

    def routed(self):
        """Generator view over the remaining routed events."""
        yield from self
