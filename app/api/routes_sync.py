import json

from fastapi import APIRouter

from app.core.config import get_settings
from app.db.repository import SyncRunRepository
from app.schemas.common import BusinessSyncRequest, BusinessSyncResponse
from app.services.provider_router import ProviderRouter
from app.services.sync_service import SyncService

router = APIRouter(prefix="/api/v1/sync", tags=["sync"])


@router.post("/ticket", response_model=BusinessSyncResponse)
async def sync_ticket(request: BusinessSyncRequest) -> BusinessSyncResponse:
    request.record_type = "ticket"
    service = SyncService()
    return await service.run(request)


@router.post("/lead", response_model=BusinessSyncResponse)
async def sync_lead(request: BusinessSyncRequest) -> BusinessSyncResponse:
    request.record_type = "lead"
    service = SyncService()
    return await service.run(request)


@router.get("/providers")
def list_providers() -> dict:
    router_service = ProviderRouter()
    return {"providers": router_service.list_providers()}


@router.get("/runs")
def list_runs(limit: int = 50) -> dict:
    settings = get_settings()
    repo = SyncRunRepository(settings.database_path)
    return {"items": repo.list_runs(limit=limit)}


@router.get("/runs/{trace_id}")
def get_run(trace_id: str) -> dict:
    settings = get_settings()
    repo = SyncRunRepository(settings.database_path)
    item = repo.get_by_trace_id(trace_id)
    if not item:
        return {"item": None}
    for key in ("request_payload", "normalized_record", "downstream_result"):
        if item.get(key):
            item[key] = json.loads(item[key])
    return {"item": item}
