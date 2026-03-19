import httpx

from app.core.config import get_settings
from app.core.exceptions import ProviderError
from app.providers.base import BaseProvider
from app.schemas.provider import ProviderEnrichmentRequest, ProviderEnrichmentResult


class OpenAIProvider(BaseProvider):
    name = "openai"

    async def enrich(self, request: ProviderEnrichmentRequest) -> ProviderEnrichmentResult:
        settings = get_settings()
        if not settings.openai_api_key:
            raise ProviderError("OPENAI_API_KEY is not configured.")

        prompt = (
            "You are a business data normalization assistant. "
            "Return JSON with summary, category, priority, recommended_actions. "
            f"Record type: {request.record_type}. Payload: {request.payload}"
        )

        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.openai_model,
            "input": prompt,
        }

        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post(
                "https://api.openai.com/v1/responses",
                headers=headers,
                json=payload,
            )

        if response.status_code >= 400:
            raise ProviderError(f"OpenAI provider failed: {response.text}")

        return ProviderEnrichmentResult(
            summary="External provider response received. Replace parsing logic for real deployment.",
            category="general",
            priority="medium",
            recommended_actions=["log_to_sheet"],
            provider_metadata={
                "provider": self.name,
                "note": "Example adapter included in scaffold; refine parsing for real use.",
            },
        )
