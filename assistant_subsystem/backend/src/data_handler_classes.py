from enum import Enum   
from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session, select
from uuid import UUID, uuid4
from dotenv import load_dotenv
from typing import Generator
import os

class Category(Enum):
    unknown = 0
    recyclable = 1
    compostable = 2
    landfill = 3


class ChatMessage(SQLModel, table=True):
    id: int = Field(primary_key=True)
    token: UUID = Field(index=True, unique=True, default_factory=uuid4)
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class RecyclingRule(SQLModel, table=True):
    id: int = Field(primary_key=True)
    region: str
    material: str
    category: Category
    instructions: Optional[str] = None


class RulesRepo:
    def __init__(self, session):
        self.session = session

    def get_rules(self):
        self.delete_old()
        return self.session.scalars(select(RulesRepo).all())    


class ChatRepo:
    def __init__(self, session, expiry, limit):
        self.session = session
        self.expiry = expiry
        self.limit = limit

    def add_new(self, token, role, content, timestamp):
        self.delete_old()
        self.session.add(ChatMessage(token, role, content, timestamp))
        self.session.commit()
    
    def get_history(self, token):
        self.delete_old()
        return self.session.execute(select(ChatMessage).where(ChatMessage.token == token).order_by(ChatMessage.timestamp.desc()).limit(self.limit))
    
    def clear_chat(self, token):
        self.delete_old()
        chat = self.session.execute(select(ChatMessage).where(ChatMessage.token == token))
        self.session.delete(chat)
        self.session.commit()
    
    def delete_old(self):
        expired = self.session.execute(select(ChatMessage).where(datetime.now() - ChatMessage.timestamp > timedelta(days=self.expiry)))
        self.session.delete(expired)
        self.session.commit()


class DBManager:
    def __init__(self, db_url):
        self.engine = create_engine(db_url, echo=True)

    def get_db(self) -> Generator[Session, None, None]:
        with Session(self.engine) as session:
            yield session