from uuid import uuid4
import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from src.data_handler_classes import ChatRepo


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


def test_history_is_oldest_first_and_limited(session):
    repo = ChatRepo(session, expiry=1, limit=2)
    token = uuid4()
    for text in ["one", "two", "three"]:
        repo.add_new(token, "user", text)
    history = repo.get_history(token)
    assert [m.content for m in history] == ["two", "three"]


def test_clear_chat_only_removes_that_session(session):
    repo = ChatRepo(session, expiry=1, limit=10)
    a, b = uuid4(), uuid4()
    repo.add_new(a, "user", "hi")
    repo.add_new(b, "user", "hello")
    repo.clear_chat(a)
    assert repo.get_history(a) == []
    assert len(repo.get_history(b)) == 1