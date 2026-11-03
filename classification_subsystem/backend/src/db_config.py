"""Read the rules database URL from the environment or a local .env file."""

import os
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]


def get_rules_db_url() -> str:
    url = os.getenv("REGIONAL_RULES_DB_URL")
    if url:
        return url

    env_file = BACKEND_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("REGIONAL_RULES_DB_URL="):
                return line.partition("=")[2].strip()

    raise RuntimeError("Set REGIONAL_RULES_DB_URL to the Neon connection URL")
