import json

import httpx

from .models import FallbackResult


class AssistantFallbackClient:
    """Adapter for the teammate's POST /fallback/classify API."""

    def __init__(self, base_url: str, timeout: float = 25.0):
        if not base_url.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def classify(
        self, image: bytes, mime_type: str, region: str, materials: list[str]
    ) -> FallbackResult:
        try:
            response = httpx.post(
                f"{self.base_url}/fallback/classify",
                files={"image": ("waste.jpg", image, mime_type)},
                data={"region": region, "materials": json.dumps(materials)},
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError):
            return FallbackResult(None)
        if not isinstance(payload, dict):
            return FallbackResult(None)
        material = payload.get("material")
        if not isinstance(material, str) or material not in materials:
            return FallbackResult(None)
        return FallbackResult(material)
