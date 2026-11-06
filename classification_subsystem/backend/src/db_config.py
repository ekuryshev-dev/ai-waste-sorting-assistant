"""Read settings from the environment or the local .env file."""

import os
from pathlib import Path


def get_setting(name: str) -> str | None:
    value = os.getenv(name)
    if value:
        return value

    env_file = Path(__file__).resolve().parents[1] / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            key, separator, value = line.partition("=")
            if separator and key.strip() == name:
                value = value.strip()
                if value[:1] == value[-1:] and value[:1] in ('"', "'"):
                    value = value[1:-1]
                return value or None

    return None


def get_rules_db_url() -> str:
    url = get_setting("REGIONAL_RULES_DB_URL")
    if url:
        return url

    raise RuntimeError("Set REGIONAL_RULES_DB_URL to the Neon connection URL")
