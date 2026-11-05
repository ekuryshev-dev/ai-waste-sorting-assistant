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
        self.set_model_path(model_path)
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def get_model_path(self) -> Path:
        return self._model_path

    def set_model_path(self, value: Path) -> None:
        path = Path(value)
        if not path.is_file():
            raise FileNotFoundError(path)
        self._model_path = path
        self.load_model()

    def load_model(self) -> None:
        model = models.resnet50(weights=None)
        model.fc = torch.nn.Linear(model.fc.in_features, len(MODEL_CLASSES))
        model.load_state_dict(torch.load(self.get_model_path(), map_location="cpu", weights_only=True))
        model.eval()
        self.model = model

    def classify(self, image: Image.Image) -> ClassificationResult:
        tensor = self.transform(image).unsqueeze(0)
        with torch.inference_mode():
            probabilities = torch.softmax(self.model(tensor), dim=1)[0]
        index = int(torch.argmax(probabilities))
        return ClassificationResult(MODEL_CLASSES[index], float(probabilities[index]))
