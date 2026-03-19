from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes_demo import router as demo_router
from app.api.routes_health import router as health_router
from app.api.routes_sync import router as sync_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.repository import SyncRunRepository

settings = get_settings()
configure_logging()
BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(_: FastAPI):
    repo = SyncRunRepository(settings.database_path)
    repo.initialize()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.3.0",
    description="Demo API orchestration service for reliable business data synchronization.",
    lifespan=lifespan,
)

app.include_router(demo_router)
app.include_router(health_router)
app.include_router(sync_router)
app.mount("/demo", StaticFiles(directory=BASE_DIR / "static" / "demo", html=True), name="demo")
