import httpx


class AnalyticsClient:
    """Send completed classifications to the dashboard service."""

    def __init__(self, base_url: str, ingest_key: str, timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.ingest_key = ingest_key
        self.timeout = timeout

    def record(self, material: str, category: str, region: str) -> bool:
        try:
            response = httpx.post(
                f"{self.base_url}/analytics/records",
                json={"item": material, "category": category, "region_code": region},
                headers={"X-Analytics-Key": self.ingest_key},
                timeout=self.timeout,
            )
            response.raise_for_status()
            return True
        except httpx.HTTPError:
            return False
