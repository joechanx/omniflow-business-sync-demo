import httpx

from app.connectors.base import BaseConnector
from app.core.config import get_settings
from app.core.exceptions import ConnectorError


class SheetsConnector(BaseConnector):
    name = "sheets"

    async def send(self, payload: dict) -> dict:
        settings = get_settings()
        if not settings.sheets_webhook_url:
            raise ConnectorError("SHEETS_WEBHOOK_URL is not configured.")

        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post(settings.sheets_webhook_url, json=payload)

        if response.status_code >= 400:
            raise ConnectorError(f"Sheets connector failed: {response.text}")

        return {"connector": self.name, "status": "success"}
