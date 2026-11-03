import json
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine, select

from .errors import RuleNotFoundError
from .models import RecyclingRule


class RegionalRulesService:
    def __init__(self, db_url: str):
        self.db_url = db_url

    @property
    def db_url(self) -> str:
        return self._db_url

    @db_url.setter
    def db_url(self, value: str) -> None:
        if not value:
            raise ValueError("db_url must not be empty")
        options = {"check_same_thread": False} if value.startswith("sqlite") else {}
        connection_url = value
        if value.startswith("postgresql://"):
            connection_url = value.replace("postgresql://", "postgresql+psycopg://", 1)
        elif value.startswith("postgres://"):
            connection_url = value.replace("postgres://", "postgresql+psycopg://", 1)
        self.engine = create_engine(connection_url, connect_args=options, pool_pre_ping=True)
        self._db_url = value

    def create_tables(self) -> None:
        SQLModel.metadata.create_all(self.engine, tables=[RecyclingRule.__table__])

    def list_regions(self) -> list[str]:
        with Session(self.engine) as session:
            return list(session.exec(select(RecyclingRule.region).distinct().order_by(RecyclingRule.region)))

    def list_materials(self, region: str) -> list[str]:
        with Session(self.engine) as session:
            return list(session.exec(
                select(RecyclingRule.material)
                .where(RecyclingRule.region == region)
                .distinct()
                .order_by(RecyclingRule.material)
            ))

    def get_rule(self, material: str, region: str) -> RecyclingRule:
        with Session(self.engine) as session:
            rule = session.exec(
                select(RecyclingRule).where(
                    RecyclingRule.material == material, RecyclingRule.region == region
                )
            ).first()
            if rule is None:
                raise RuleNotFoundError(f"No rule for {material!r} in {region!r}")
            session.expunge(rule)
            return rule

    def import_json(self, path: Path) -> int:
        """Add or update rules without changing the application code."""
        records = json.loads(Path(path).read_text(encoding="utf-8"))
        with Session(self.engine) as session:
            for record in records:
                existing = session.exec(
                    select(RecyclingRule).where(
                        RecyclingRule.region == record["region"],
                        RecyclingRule.material == record["material"],
                    )
                ).first()
                if existing is None:
                    session.add(RecyclingRule(**record))
                else:
                    for field in ("category", "instructions"):
                        setattr(existing, field, record[field])
            session.commit()
        return len(records)
