from fastapi import APIRouter

from app.utils.responses import success_response

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return success_response(
        message="Service is healthy",
        data={"status": "ok"},
    )
