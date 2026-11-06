"""Send uncertain images to the AI assistant API."""

import httpx

from .models import Category, FallbackResult


class AssistantFallbackClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def classify(self, image: bytes, mime_type: str, region: str) -> FallbackResult:
        try:
            response = httpx.post(
                f"{self.base_url}/fallback/classify",
                files={"image": ("waste.jpg", image, mime_type)},
                data={"region": region},
                timeout=25.0,
            )
            response.raise_for_status()
            data = response.json()
            category = Category(data["category"])
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            return FallbackResult()

        instructions = data.get("instructions")
        if not isinstance(instructions, str) or not instructions.strip():
            instructions = None
        material = data.get("material")
        if not isinstance(material, str):
            material = None
        return FallbackResult(category, material, instructions)
