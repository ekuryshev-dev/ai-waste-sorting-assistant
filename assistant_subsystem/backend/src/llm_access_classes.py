from abc import ABC, abstractmethod


class LLMClientInter(ABC):
    @abstractmethod
    def converse(self, messages) -> str: pass


class LLMMockClient(LLMClientInter):
    def __init__ (self):
        self.reply = "Mock reply"
        self.received = []

    def converse(self, messages):
        self.received = messages
        return self.reply


class OpenAIClient(LLMClientInter):
    def __init__ (self, model, timeout, api):
        self.model = model
        self.timeout = timeout
        self.api = api

    def converse(self, messages):
        raise NotImplementedError("Real API call comes later")