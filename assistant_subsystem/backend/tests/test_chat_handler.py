from chat_handler_classes import AssistantService, PromptBuilder
from data_handler_classes import RecyclingRule, RulesRepo, ChatRepo, Category
from llm_access_classes import LLMMockClient
from uuid import uuid4


def chat_history_get_and_clear(tst_sess):
    service = AssistantService(RulesRepo(tst_sess), ChatRepo(tst_sess, 1, 10), LLMMockClient(), PromptBuilder("Mock prompt"))
    token = uuid4()
    service.converse(token, "Mock question")
    roles = [m.role for m in service.get_history(token)]
    assert roles == ["user", "assistant"]
    service.clear_chat(token)
    assert not service.get_history(token)
    

def test_both_messages_are_processed(tst_sess):
    llm = LLMMockClient()
    service = AssistantService(RulesRepo(tst_sess), ChatRepo(tst_sess, 1, 10), llm, PromptBuilder("Mock prompt"))
    response = service.converse(uuid4(), "Mock question")
    assert "Mock question" in llm.received[0]["content"]
    assert "user" in llm.received[0]["role"]
    assert response == "Mock reply"


def test_build_the_prompt(tst_sess):
    tst_sess.add(RecyclingRule(region="DE", material="paper", category=Category.recyclable))
    tst_sess.commit()
    service = AssistantService(RulesRepo(tst_sess), ChatRepo(tst_sess, 1, 10), LLMMockClient(), PromptBuilder("Mock prompt"))
    rules = service.rules_repo.get_rules()
    messages = service.prompt_builder.build([], rules, "Mock question")
    assert messages == [{"role": "system", "content": "Mock prompt\n\nRecycling rules:\n- DE | paper: recyclable"}, {"role": "user", "content": "Mock question"}]