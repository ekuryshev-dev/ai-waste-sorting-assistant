import json
from pathlib import Path

from .models import Category


class RegionalRulesService:
    """Read disposal rules from a JSON file."""

    def __init__(self, rules_path: Path):
        self.set_rules_path(rules_path)

    def get_rules_path(self) -> Path:
        return self._rules_path

    def set_rules_path(self, value: Path) -> None:
        path = Path(value)
        if not path.is_file():
            raise FileNotFoundError(path)
        self._rules_path = path
        self.load_rules()

    def load_rules(self) -> None:
        rows = json.loads(self.get_rules_path().read_text(encoding="utf-8"))
        self.rules = rows

    def list_regions(self) -> list[str]:
        regions = []
        for row in self.rules:
            if row["region"] not in regions:
                regions.append(row["region"])
        return sorted(regions)

    def get_rule(self, material: str, region: str) -> tuple[Category, str]:
        for row in self.rules:
            if row["region"] == region and row["material"] == material:
                return Category(row["category"]), row["instructions"]
        raise KeyError((region, material))
