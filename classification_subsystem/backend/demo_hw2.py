"""Homework 2 demo: classify image events and write two JSONL files."""

from pathlib import Path

from src.image_processing import ImageProcessor
from src.stream_processing import (
    ConfidenceFilter,
    ImageClassifierProcessor,
    JsonlWriter,
    PredictionStream,
    image_paths,
)
from src.wasteclassifier import WasteClassifier


BASE = Path(__file__).resolve().parent
THRESHOLD = 0.7


def main() -> None:
    output_dir = BASE / "output"
    output_dir.mkdir(exist_ok=True)
    all_path = output_dir / "all_predictions.jsonl"
    accepted_path = output_dir / "accepted_predictions.jsonl"
    all_path.write_text("", encoding="utf-8")
    accepted_path.write_text("", encoding="utf-8")

    classifier = WasteClassifier(BASE / "model" / "resnet50_garbage_classificationv1.2.pth")
    all_writer = JsonlWriter(all_path)
    accepted_writer = JsonlWriter(accepted_path)
    pipeline = (
        ImageClassifierProcessor(classifier, ImageProcessor(), THRESHOLD)
        | all_writer
        | ConfidenceFilter()
        | accepted_writer
    )
    stream = PredictionStream(image_paths(BASE / "examples"), pipeline)
    for _ in stream:
        pass  # Processing and writing happen inside the pipeline.

    print(f"Processed: {all_writer.count} images")
    print(f"Above {THRESHOLD:.0%} confidence: {accepted_writer.count} images")
    print(f"All predictions: {all_path}")
    print(f"Accepted predictions: {accepted_path}")


if __name__ == "__main__":
    main()
