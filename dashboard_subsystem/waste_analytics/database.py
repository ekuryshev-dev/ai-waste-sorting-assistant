
import os
import ssl

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

use_sqlite = os.getenv("USE_SQLITE", "0")

if use_sqlite == "1":
    database_url = "sqlite:///./analytics_local.db"

    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False}
    )

else:
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is missing")

    database_url = database_url.replace(
        "postgresql+psycopg://",
        "postgresql+pg8000://",
        1
    ).replace(
        "postgresql://",
        "postgresql+pg8000://",
        1
    )

    database_url = database_url.split("?", 1)[0]

    engine = create_engine(
        database_url,
        connect_args={"ssl_context": ssl.create_default_context()},
        pool_pre_ping=True
    )
