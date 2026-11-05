from abc import ABC, abstractmethod
from openai import OpenAI


class LLMClientInter(ABC):
    @abstractmethod
    def converse(self, messages) -> str: pass


class LLMMockClient(LLMClientInter):
    def __init__(self, reply = "Mock reply"):
        self.reply = reply
        self._received = []
        self.calls = 0

    @property
    def received(self):
        return self._received

    def converse(self, messages):
        self._received = messages
        self.calls += 1
        return self.reply


class OpenAIClient(LLMClientInter):
    def __init__(self, model, timeout, api):
        self.model = model
        self.timeout = timeout
        self.client = OpenAI(api_key=api, timeout=self.timeout, max_retries=1)

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        if not value:
            raise ValueError("model name must not be empty")
        self._model = value

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        if value <= 0:
            raise ValueError("timeout must be more than 0 seconds")
        self._timeout = value
        if hasattr(self, "client"):
            self.client = self.client.with_options(timeout=value)

    def converse(self, messages):
        response = self.client.chat.completions.create(model=self.model, messages=messages)
        return response.choices[0].message.content or ""