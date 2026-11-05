import argparse
from pathlib import Path

from src.class_mapping import ClassMapping
from src.engine import DisposalRecommendationEngine
from src.image_processing import ImageProcessor
from src.models import ImageQuery
from src.regional_rules import RegionalRulesService
from src.wasteclassifier import WasteClassifier


BASE = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description="Homework 1 waste classification demo")
    parser.add_argument("path", nargs="?", type=Path, default=BASE / "examples",
                        help="An image file or a directory of images (default: examples)")
    parser.add_argument("--region", default="Dortmund")
    args = parser.parse_args()

    engine = DisposalRecommendationEngine(
        WasteClassifier(BASE / "model" / "resnet50_garbage_classificationv1.2.pth"),
        RegionalRulesService(BASE / "regional_rules_2026.json"),
        ClassMapping(BASE / "class_mapping.json"),
        ImageProcessor(),
    )
    image_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    if args.path.is_dir():
        images = sorted(path for path in args.path.iterdir()
                        if path.is_file() and path.suffix.lower() in image_extensions)
    elif args.path.is_file() and args.path.suffix.lower() in image_extensions:
        images = [args.path]
    else:
        parser.error("Provide a directory or a JPEG, PNG or WebP image")
    if not images:
        parser.error("No JPEG, PNG or WebP images found")

    for image_path in images:
        result = engine.get_recommendation(
            ImageQuery(image_path.read_bytes(), args.region)
        )
        print(f"\nImage: {image_path.name}")
        print(f"Status: {result.get_status()}")
        if result.classification is not None:
            print(f"Material: {result.classification.waste_class}")
            print(f"Confidence: {result.classification.get_confidence():.1%}")
        print(f"Category: {result.category.value}")
        print(f"Recommendation: {result.message}")


if __name__ == "__main__":
    main()
