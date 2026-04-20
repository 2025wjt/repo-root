from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_project_service
from app.services.project_service import ProjectService
from app.utils.responses import success_response

router = APIRouter()


@router.get("/projects/{project_id}/events")
def list_project_events(
    project_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    service: ProjectService = Depends(get_project_service),
):
    events = service.list_events(project_id=project_id, limit=limit)
    return success_response(
        message="操作成功",
        data=[event.model_dump() for event in events],
    )
