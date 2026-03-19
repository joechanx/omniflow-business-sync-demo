from app.connectors.github_connector import GitHubConnector
from app.connectors.sheets_connector import SheetsConnector
from app.connectors.slack_connector import SlackConnector
from app.connectors.webhook_connector import WebhookConnector
from app.core.config import get_settings


class ConnectorService:
    def __init__(self) -> None:
        settings = get_settings()
        self.settings = settings
        self.connectors = []

        if settings.enable_connectors:
            if settings.enable_slack_connector:
                self.connectors.append(SlackConnector())
            if settings.enable_github_connector:
                self.connectors.append(GitHubConnector())
            if settings.enable_sheets_connector:
                self.connectors.append(SheetsConnector())
            if settings.enable_webhook_connector:
                self.connectors.append(WebhookConnector())

    async def fan_out(self, payload: dict) -> list[dict]:
        results = []
        for connector in self.connectors:
            try:
                result = await connector.send(payload)
                results.append(result)
            except Exception as exc:
                results.append(
                    {
                        "connector": connector.name,
                        "status": "failed",
                        "error": str(exc),
                    }
                )
        return results
