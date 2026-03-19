from app.providers.base import BaseProvider
from app.schemas.provider import ProviderEnrichmentRequest, ProviderEnrichmentResult


class MockProvider(BaseProvider):
    name = "mock"

    async def enrich(self, request: ProviderEnrichmentRequest) -> ProviderEnrichmentResult:
        payload = request.payload
        text = " ".join(str(v) for v in payload.values()).lower()

        if "invoice" in text or "billing" in text or "charge" in text:
            category = "billing"
        elif "bug" in text or "error" in text or "crash" in text:
            category = "technical"
        elif request.record_type == "lead":
            category = "sales"
        else:
            category = "general"

        if "urgent" in text or "high" in text or "asap" in text:
            priority = "high"
        elif "low" in text:
            priority = "low"
        else:
            priority = "medium"

        if request.record_type == "ticket":
            summary = payload.get("description") or payload.get("subject") or "Support ticket received."
            actions = ["notify_support", "create_issue", "log_to_sheet"]
        else:
            summary = payload.get("notes") or payload.get("company") or "Lead captured."
            actions = ["score_lead", "notify_sales", "log_to_sheet"]

        return ProviderEnrichmentResult(
            summary=summary[:160],
            category=category,
            priority=priority,
            recommended_actions=actions,
            provider_metadata={"provider": self.name, "mode": "heuristic-demo"},
        )
