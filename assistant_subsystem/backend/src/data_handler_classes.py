from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional
from uuid import UUID
from sqlmodel import Field, Session, SQLModel, create_engine, delete, select, col


class Category(str, Enum):
    unknown = "unknown"
    recyclable = "recyclable"
    compostable = "compostable"
    landfill = "landfill"
    

class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    token: UUID = Field(index=True)
    role: str
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)


class RecyclingRule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    region: str = Field(index=True)
    material: str
    category: Category
    instructions: Optional[str] = None


class RulesRepo:
    def __init__(self, session):
        self.session = session

    def get_rules(self, region=None):
        stmt = select(RecyclingRule)
        if region is not None:
            stmt = stmt.where(col(RecyclingRule.region) == region)
        return self.session.exec(stmt).all()


class ChatRepo:
    def __init__(self, session, expiry, limit):
        self.session = session
        self.expiry = expiry
        self.limit = limit

    @property
    def expiry(self):
        return self._expiry

    @expiry.setter
    def expiry(self, value):
        if value <= 0:
            raise ValueError("expiry must be more than 0 days")
        self._expiry = value

    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, value):
        if value <= 0:
            raise ValueError("limit must be more than 0")
        self._limit = value

    def add_new(self, token, role, content):
        self.delete_old()
        self.session.add(ChatMessage(token=token, role=role, content=content))
        self.session.commit()

    def get_history(self, token):
        self.delete_old()
        stmt = (
            select(ChatMessage)
            .where(col(ChatMessage.token) == token)
            .order_by(col(ChatMessage.timestamp).desc(), col(ChatMessage.id).desc())
            .limit(self.limit)
        )
        return list(reversed(self.session.exec(stmt).all()))

    def clear_chat(self, token):
        self.delete_old()
        self.session.execute(delete(ChatMessage).where(col(ChatMessage.token) == token))
        self.session.commit()

    def delete_old(self):
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.expiry)
        self.session.execute(delete(ChatMessage).where(col(ChatMessage.timestamp) < cutoff))
        self.session.commit()


class DBManager:
    def __init__(self, db_url):
        self.engine = create_engine(db_url, echo=False, pool_pre_ping=True)

    def create_tables(self):
        SQLModel.metadata.create_all(self.engine)

    def get_db(self):
        with Session(self.engine) as session:
            yield session