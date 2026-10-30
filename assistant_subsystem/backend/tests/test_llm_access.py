import pytest
from llm_access_classes import LLMClientInter, LLMMockClient


def test_mock_returns_fixed_reply():
    client = LLMMockClient()
    assert client.converse([{"role": "user", "content": "message"}]) == "Mock reply"


def test_mock_records_received_messages():
    client = LLMMockClient()
    msgs = [{"role": "user", "content": "message"}]
    client.converse(msgs)
    assert client.received == msgs


def test_interface_cannot_be_instantiated():
    with pytest.raises(TypeError):
        LLMClientInter() # type: ignore