import httpx

from app.core.config import get_settings


class WorkflowService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def trigger(self, payload: dict) -> dict:
        if not self.settings.n8n_webhook_url:
            return {"status": "skipped", "reason": "N8N_WEBHOOK_URL not configured"}

        async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
            response = await client.post(self.settings.n8n_webhook_url, json=payload)

        return {
            "status": "success" if response.status_code < 400 else "failed",
            "status_code": response.status_code,
            "body_preview": response.text[:300],
        }
