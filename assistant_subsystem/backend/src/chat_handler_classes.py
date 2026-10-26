from data_handler_classes import RulesRepo, ChatRepo
from llm_access_classes import OpenAIClient
from config import ai_api, ai_model, ai_timeout, message_limit, chat_expiry, db_manager


class PromptBuilder:
    def __init__(self):
        self.system_prompt = ""

    def build(self, history, rules):
        system_message = self.system_prompt + rules
        messages = [{"role": "system", "content": system_message}] + history
        return messages

class AssistantService:
    def __init__(self):
        self.rules_repo = RulesRepo(db_manager.get_db())
        self.chat_repo = ChatRepo(db_manager.get_db(), chat_expiry, message_limit)
        self.ai_client = OpenAIClient(ai_model, ai_timeout, ai_api)
        self.prompt_builder = PromptBuilder()

    def converse(self, token, message):
        self.chat_repo.add_new(token, "user", message)
        history = self.chat_repo.get_history(token)
        rules = self.rules_repo.get_rules()
        messages = self.promp_builder.build(history, rules)
        return self.ai_client.converse(messages)

    def get_history(self, token):
        return self.chat_repo.get_history(token)

    def clear_chat(self, token):
        self.chat_repo.clear_chat(token)