import httpx

from app.connectors.base import BaseConnector
from app.core.config import get_settings
from app.core.exceptions import ConnectorError


class SlackConnector(BaseConnector):
    name = "slack"

    async def send(self, payload: dict) -> dict:
        settings = get_settings()
        if not settings.slack_webhook_url:
            raise ConnectorError("SLACK_WEBHOOK_URL is not configured.")

        body = {
            "text": f"[{payload.get('priority', 'unknown').upper()}] "
                    f"{payload.get('record_type')} from {payload.get('source_system')}: "
                    f"{payload.get('summary')}"
        }

        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post(settings.slack_webhook_url, json=body)

        if response.status_code >= 400:
            raise ConnectorError(f"Slack webhook failed: {response.text}")

        return {"connector": self.name, "status": "success"}
