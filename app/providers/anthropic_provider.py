import httpx

from app.core.config import get_settings
from app.core.exceptions import ProviderError
from app.providers.base import BaseProvider
from app.schemas.provider import ProviderEnrichmentRequest, ProviderEnrichmentResult


class AnthropicProvider(BaseProvider):
    name = "anthropic"

    async def enrich(self, request: ProviderEnrichmentRequest) -> ProviderEnrichmentResult:
        settings = get_settings()
        if not settings.anthropic_api_key:
            raise ProviderError("ANTHROPIC_API_KEY is not configured.")

        headers = {
            "x-api-key": settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.anthropic_model,
            "max_tokens": 300,
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Normalize this business record into JSON with summary, "
                        "category, priority, recommended_actions. "
                        f"Record type: {request.record_type}. Payload: {request.payload}"
                    ),
                }
            ],
        }

        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
            )

        if response.status_code >= 400:
            raise ProviderError(f"Anthropic provider failed: {response.text}")

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
