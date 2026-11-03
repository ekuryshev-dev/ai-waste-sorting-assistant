"""Create and fill only the classification subsystem's regional-rules table."""

import json
from pathlib import Path

from .src.db_config import get_rules_db_url
from .src.regional_rules import RegionalRulesService


DATA_FILE = Path(__file__).parent / "regional_rules_2026.json"


def main() -> None:
    records = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    pairs = [(row["region"], row["material"]) for row in records]
    categories = {"recyclable", "compostable", "landfill"}
    if (len(records) != 120 or len(set(pairs)) != 120
            or any(row["category"] not in categories or not row["instructions"].strip()
                   for row in records)):
        raise ValueError("The regional dataset failed validation")

    rules = RegionalRulesService(get_rules_db_url())
    rules.create_tables()
    rules.import_json(DATA_FILE)
    print(f"Imported {len(records)} rules for {len(rules.list_regions())} regions")


if __name__ == "__main__":
    main()
