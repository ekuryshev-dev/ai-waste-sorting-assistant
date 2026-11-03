from pathlib import Path

import torch
from PIL import Image
from torchvision import models, transforms

from .models import ClassificationResult


MODEL_CLASSES = (
    "battery", "biological", "brown-glass", "cardboard", "clothes",
    "green-glass", "metal", "paper", "plastic", "shoes", "trash", "white-glass",
)


class WasteClassifier:
    def __init__(self, model_path: Path):
        self.model_path = Path(model_path)
        self.model = None
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        self.load_model()

    @property
    def model_path(self) -> Path:
        return self._model_path

    @model_path.setter
    def model_path(self, value: Path) -> None:
        path = Path(value)
        if not path.is_file():
            raise FileNotFoundError(f"Model weights not found: {path}")
        self._model_path = path

    def load_model(self) -> None:
        model = models.resnet50(weights=None)
        model.fc = torch.nn.Linear(model.fc.in_features, len(MODEL_CLASSES))
        weights = torch.load(self.model_path, map_location="cpu", weights_only=True)
        model.load_state_dict(weights)
        model.eval()
        self.model = model

    def classify(self, image: Image.Image) -> ClassificationResult:
        if image.size != (224, 224) or image.mode != "RGB":
            raise ValueError("Image must be 224 x 224 RGB")
        tensor = self.transform(image).unsqueeze(0)
        with torch.inference_mode():
            probabilities = torch.softmax(self.model(tensor), dim=1)[0]
        index = int(torch.argmax(probabilities))
        return ClassificationResult(MODEL_CLASSES[index], float(probabilities[index]), "cv")
