import json
import logging

from app.core.config import get_settings
from app.core.tracing import generate_trace_id, stable_payload_hash
from app.db.repository import SyncRunRepository
from app.schemas.common import (
    BusinessSyncRequest,
    BusinessSyncResponse,
    DownstreamResult,
    NormalizedRecord,
)
from app.schemas.provider import ProviderEnrichmentRequest, ProviderEnrichmentResult
from app.services.connector_service import ConnectorService
from app.services.provider_router import ProviderRouter
from app.services.workflow_service import WorkflowService

logger = logging.getLogger(__name__)


class SyncService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.repo = SyncRunRepository(self.settings.database_path)
        self.repo.initialize()
        self.providers = ProviderRouter()
        self.workflow_service = WorkflowService()
        self.connector_service = ConnectorService()

    def _build_idempotency_key(self, request: BusinessSyncRequest) -> str:
        if request.idempotency_key:
            return request.idempotency_key
        payload_hash = stable_payload_hash(request.payload)
        return f"{request.source_system}:{request.source_record_id}:{payload_hash[:12]}"

    async def _enrich_with_fallback(
        self,
        request: BusinessSyncRequest,
    ) -> tuple[ProviderEnrichmentResult, list[dict[str, str]]]:
        attempts: list[dict[str, str]] = []
        last_exc: Exception | None = None

        for provider in self.providers.resolve_chain(request.provider):
            try:
                enrichment = await provider.enrich(
                    ProviderEnrichmentRequest(
                        record_type=request.record_type,
                        source_system=request.source_system,
                        source_record_id=request.source_record_id,
                        payload=request.payload,
                    )
                )
                attempts.append({"provider": provider.name, "status": "success"})
                return enrichment, attempts
            except Exception as exc:  # pragma: no cover - exercised by fallback tests via response data
                attempts.append({"provider": provider.name, "status": "failed", "error": str(exc)})
                last_exc = exc
                logger.warning("Provider attempt failed: provider=%s error=%s", provider.name, exc)

        if last_exc:
            raise last_exc
        raise RuntimeError("No providers available for enrichment.")

    async def run(self, request: BusinessSyncRequest) -> BusinessSyncResponse:
        idempotency_key = self._build_idempotency_key(request)
        existing = self.repo.get_by_idempotency_key(idempotency_key)

        if existing and existing.get("status") == "success":
            normalized_record = json.loads(existing["normalized_record"]) if existing.get("normalized_record") else None
            downstream_result = json.loads(existing["downstream_result"]) if existing.get("downstream_result") else None
            return BusinessSyncResponse(
                status="success",
                trace_id=existing["trace_id"],
                idempotent_replay=True,
                normalized_record=normalized_record,
                downstream=downstream_result,
            )

        trace_id = generate_trace_id()
        requested_provider = request.provider or self.settings.default_provider

        self.repo.create_run(
            trace_id=trace_id,
            idempotency_key=idempotency_key,
            source_system=request.source_system,
            source_record_id=request.source_record_id,
            record_type=request.record_type,
            provider=requested_provider,
            request_payload=request.model_dump(),
        )

        try:
            enrichment, provider_attempts = await self._enrich_with_fallback(request)

            normalized_record = NormalizedRecord(
                record_type=request.record_type,
                source_system=request.source_system,
                source_record_id=request.source_record_id,
                summary=enrichment.summary,
                category=enrichment.category,
                priority=enrichment.priority,
                recommended_actions=enrichment.recommended_actions,
                raw_enrichment={
                    **enrichment.provider_metadata,
                    "requested_provider": requested_provider,
                    "provider_attempts": provider_attempts,
                    "provider_used": next(
                        (attempt["provider"] for attempt in provider_attempts if attempt["status"] == "success"),
                        requested_provider,
                    ),
                    "fallback_used": len(provider_attempts) > 1,
                },
            )

            workflow_result = await self.workflow_service.trigger(normalized_record.model_dump())
            connector_results = await self.connector_service.fan_out(normalized_record.model_dump())

            downstream = DownstreamResult(
                workflow=workflow_result,
                connectors=connector_results,
            )

            self.repo.mark_success(
                trace_id,
                normalized_record=normalized_record.model_dump(),
                downstream_result=downstream.model_dump(),
            )

            return BusinessSyncResponse(
                status="success",
                trace_id=trace_id,
                idempotent_replay=False,
                normalized_record=normalized_record,
                downstream=downstream,
            )

        except Exception as exc:
            logger.exception("Sync failed for trace_id=%s", trace_id)
            self.repo.mark_failed(trace_id, str(exc))
            return BusinessSyncResponse(
                status="failed",
                trace_id=trace_id,
                idempotent_replay=False,
                error_message=str(exc),
            )
