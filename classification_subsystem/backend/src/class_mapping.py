import json
from pathlib import Path


class ClassMapping:
    """Translate model labels into material names used by regional rules."""

    def __init__(self, path: Path):
        self.set_path(path)

    def get_path(self) -> Path:
        return self._path

    def set_path(self, value: Path) -> None:
        path = Path(value)
        if not path.is_file():
            raise FileNotFoundError(path)
        self._path = path
        self.reload()

    def reload(self) -> None:
        data = json.loads(self.get_path().read_text(encoding="utf-8"))
        self.model_classes = data["model_classes"]

    def from_model(self, label: str) -> str | None:
        return self.model_classes.get(label)
