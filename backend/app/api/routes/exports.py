from fastapi import APIRouter, Depends

from app.api.dependencies import get_export_service
from app.schemas.projects import ExportProjectRequest
from app.services.export_service import ExportService
from app.utils.responses import success_response

router = APIRouter()


@router.post("/projects/{project_id}/export")
def export_project(
    project_id: str,
    payload: ExportProjectRequest,
    service: ExportService = Depends(get_export_service),
):
    export_result = service.export_project(
        project_id=project_id,
        export_type=payload.export_type,
    )
    return success_response(message="导出成功", data=export_result)
