import httpx

from app.connectors.base import BaseConnector
from app.core.config import get_settings
from app.core.exceptions import ConnectorError


class GitHubConnector(BaseConnector):
    name = "github"

    async def send(self, payload: dict) -> dict:
        settings = get_settings()
        if not settings.github_token or not settings.github_repo:
            raise ConnectorError("GitHub connector is not configured.")

        api_url = settings.github_api_url or f"https://api.github.com/repos/{settings.github_repo}/issues"
        headers = {
            "Authorization": f"Bearer {settings.github_token}",
            "Accept": "application/vnd.github+json",
        }
        body = {
            "title": f"[{payload.get('priority', 'medium')}] {payload.get('source_record_id')}",
            "body": (
                f"Source system: {payload.get('source_system')}\n\n"
                f"Summary: {payload.get('summary')}\n\n"
                f"Category: {payload.get('category')}\n"
            ),
            "labels": [payload.get("category", "general"), payload.get("priority", "medium")],
        }

        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post(api_url, headers=headers, json=body)

        if response.status_code >= 400:
            raise ConnectorError(f"GitHub issue creation failed: {response.text}")

        return {"connector": self.name, "status": "success"}
