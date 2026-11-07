from sqlmodel import Session, create_engine, select

from .errors import ClassificationError
from .models import Category, RecyclingRule


class RegionalRulesService:
    """Read disposal rules from our table in Neon/PostgreSQL."""

    def __init__(self, db_url: str):
        self.set_db_url(db_url)

    def get_db_url(self) -> str:
        return self._db_url

    def set_db_url(self, value: str) -> None:
        self._db_url = value
        connection_url = value.replace("postgresql://", "postgresql+psycopg://", 1)
        connection_url = connection_url.replace("postgres://", "postgresql+psycopg://", 1)
        self.engine = create_engine(connection_url, pool_pre_ping=True)

    def list_regions(self) -> list[str]:
        with Session(self.engine) as session:
            statement = select(RecyclingRule.region).distinct().order_by(RecyclingRule.region)
            return list(session.exec(statement))

    def get_rule(self, material: str, region: str) -> tuple[Category, str]:
        with Session(self.engine) as session:
            statement = select(RecyclingRule).where(
                RecyclingRule.material == material,
                RecyclingRule.region == region,
            )
            rule = session.exec(statement).first()
            if rule is None:
                raise ClassificationError("No disposal rule for this material and region", 422)
            return rule.category, rule.instructions or ""
