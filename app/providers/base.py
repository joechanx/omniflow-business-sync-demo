from abc import ABC, abstractmethod

from app.schemas.provider import ProviderEnrichmentRequest, ProviderEnrichmentResult


class BaseProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def enrich(self, request: ProviderEnrichmentRequest) -> ProviderEnrichmentResult:
        raise NotImplementedError
