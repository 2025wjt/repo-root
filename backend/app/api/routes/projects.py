from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from app.api.dependencies import get_project_service
from app.schemas.projects import CreateProjectRequest
from app.services.project_service import ProjectService
from app.utils.responses import success_response

router = APIRouter()


@router.post("/projects")
def create_project(
    payload: CreateProjectRequest,
    service: ProjectService = Depends(get_project_service),
):
    project = service.create_project(payload)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=success_response(
            message="项目创建成功",
            data={
                "project_id": project.project_id,
                "status": project.status,
                "current_stage": project.current_stage,
            },
        ),
    )


@router.get("/projects/{project_id}")
def get_project(
    project_id: str,
    service: ProjectService = Depends(get_project_service),
):
    project = service.get_project(project_id)
    return success_response(message="操作成功", data=project.model_dump())


@router.get("/projects/{project_id}/overview")
def get_project_overview(
    project_id: str,
    service: ProjectService = Depends(get_project_service),
):
    overview = service.get_overview(project_id)
    return success_response(message="操作成功", data=overview)


@router.get("/projects/{project_id}/tasks")
def list_project_tasks(
    project_id: str,
    stage: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    service: ProjectService = Depends(get_project_service),
):
    tasks = service.list_tasks(project_id=project_id, stage=stage, status=status_filter)
    return success_response(
        message="操作成功",
        data=[task.model_dump() for task in tasks],
    )
