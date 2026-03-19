from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter(tags=["demo"])


@router.get("/", include_in_schema=False)
def root_redirect() -> RedirectResponse:
    return RedirectResponse(url="/demo/")
