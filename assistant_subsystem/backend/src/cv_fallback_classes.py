import base64
import json
from dataclasses import dataclass
from data_handler_classes import Category
from errors import LLMError


@dataclass
class FallbackResult:
    category: Category
    material: str | None = None
    instructions: str | None = None


class ImageFallbackClassifier:
    def __init__(self, ai_client, rules_repo, prompt_builder, max_retries = 2):
        self.ai_client = ai_client
        self.rules_repo = rules_repo
        self.prompt_builder = prompt_builder
        self.max_retries = max_retries

    def classify(self, image, mime_type = "image/jpeg", region = None):
        messages = self.build_messages(image, mime_type, region)
        for _ in range(self.max_retries + 1):
            try:
                reply = self.ai_client.converse(messages)
            except LLMError:
                break
            result = self.parse(reply)
            if (result is not None) and (result.category != Category.unknown):
                return result
        return FallbackResult(Category.unknown)

    def build_messages(self, image, mime_type, region=None):
        rules = None if region is None else self.rules_repo.get_rules(region)
        encoded = base64.b64encode(image).decode()
        request = [{"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{encoded}"}}]
        return self.prompt_builder.build(None, rules, request)

    def parse(self, reply):
        start, end = reply.find("{"), reply.rfind("}")
        try:
            data = json.loads(reply[start:end + 1])
            category = Category[str(data["category"]).strip().lower()]
        except (ValueError, KeyError):
            return None
        return FallbackResult(category, data.get("material"), data.get("instructions"))