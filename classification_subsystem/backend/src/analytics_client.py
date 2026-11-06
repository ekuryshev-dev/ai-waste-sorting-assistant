"""Send confident CV results to the analytics API."""

import httpx


class AnalyticsClient:
    def __init__(self, base_url: str, ingest_key: str):
        self.base_url = base_url.rstrip("/")
        self.ingest_key = ingest_key

    def record(self, material: str, category: str, region: str) -> bool:
        try:
            response = httpx.post(
                f"{self.base_url}/analytics/records",
                json={"item": material, "category": category, "region_code": region},
                headers={"X-Analytics-Key": self.ingest_key},
                timeout=5.0,
            )
            response.raise_for_status()
            return True
        except httpx.HTTPError:
            return False
