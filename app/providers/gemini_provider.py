import httpx

from app.core.config import get_settings
from app.core.exceptions import ProviderError
from app.providers.base import BaseProvider
from app.schemas.provider import ProviderEnrichmentRequest, ProviderEnrichmentResult


class GeminiProvider(BaseProvider):
    name = "gemini"

    async def enrich(self, request: ProviderEnrichmentRequest) -> ProviderEnrichmentResult:
        settings = get_settings()
        if not settings.gemini_api_key:
            raise ProviderError("GEMINI_API_KEY is not configured.")

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{settings.gemini_model}:generateContent?key={settings.gemini_api_key}"
        )
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                "Normalize this business record into JSON with summary, "
                                "category, priority, recommended_actions. "
                                f"Record type: {request.record_type}. Payload: {request.payload}"
                            )
                        }
                    ]
                }
            ]
        }

        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post(url, json=payload)

        if response.status_code >= 400:
            raise ProviderError(f"Gemini provider failed: {response.text}")

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
