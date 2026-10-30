from abc import ABC, abstractmethod
from openai import OpenAI, OpenAIError
from errors import LLMError


class LLMClientInter(ABC):
    @abstractmethod
    def converse(self, messages) -> str: pass


class LLMMockClient(LLMClientInter):
    def __init__(self, reply = "Mock reply"):
        self.reply = reply
        self.received = []
        self.calls = 0

    def converse(self, messages):
        self.received = messages
        self.calls += 1
        return self.reply


class OpenAIClient(LLMClientInter):
    def __init__(self, model, timeout, api):
        self.model = model
        self.client = OpenAI(api_key=api, timeout=timeout)

    def converse(self, messages):
        try:
            response = self.client.chat.completions.create(model=self.model, messages=messages)
        except OpenAIError as e:
            raise LLMError(str(e)) from e
        return response.choices[0].message.content or ""