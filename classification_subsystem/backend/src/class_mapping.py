import json
from pathlib import Path


class ClassMapping:
    """Maps CV model labels to material names used in regional rules."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.reload()

    def reload(self) -> None:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.model_classes = data["model_classes"]

    def from_model(self, label: str) -> str | None:
        return self.model_classes.get(label)
