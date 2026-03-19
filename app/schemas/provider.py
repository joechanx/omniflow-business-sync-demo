from typing import Any

from pydantic import BaseModel


class ProviderEnrichmentRequest(BaseModel):
    record_type: str
    source_system: str
    source_record_id: str
    payload: dict[str, Any]


class ProviderEnrichmentResult(BaseModel):
    summary: str
    category: str
    priority: str
    recommended_actions: list[str]
    provider_metadata: dict[str, Any]
