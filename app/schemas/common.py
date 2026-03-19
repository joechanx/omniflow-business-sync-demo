from typing import Any, Literal

from pydantic import BaseModel, Field


class BusinessSyncRequest(BaseModel):
    source_system: str = Field(..., examples=["zendesk"])
    source_record_id: str = Field(..., examples=["TICKET-10021"])
    record_type: Literal["ticket", "lead"]
    provider: str | None = Field(default=None, examples=["mock"])
    idempotency_key: str | None = None
    payload: dict[str, Any]


class NormalizedRecord(BaseModel):
    record_type: str
    source_system: str
    source_record_id: str
    summary: str
    category: str
    priority: str
    recommended_actions: list[str]
    raw_enrichment: dict[str, Any] = Field(default_factory=dict)


class DownstreamResult(BaseModel):
    workflow: dict[str, Any]
    connectors: list[dict[str, Any]]


class BusinessSyncResponse(BaseModel):
    status: Literal["success", "failed"]
    trace_id: str
    idempotent_replay: bool = False
    normalized_record: NormalizedRecord | None = None
    downstream: DownstreamResult | None = None
    error_message: str | None = None
