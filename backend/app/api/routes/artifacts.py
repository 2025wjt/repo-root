from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_artifact_service, get_project_service
from app.services.artifact_service import ArtifactService
from app.services.project_service import ProjectService
from app.utils.responses import success_response

router = APIRouter()


@router.get("/projects/{project_id}/artifacts")
def list_project_artifacts(
    project_id: str,
    artifact_type: str | None = Query(default=None),
    service: ProjectService = Depends(get_project_service),
):
    artifacts = service.list_artifacts(project_id=project_id, artifact_type=artifact_type)
    return success_response(
        message="操作成功",
        data=[artifact.model_dump() for artifact in artifacts],
    )


@router.get("/projects/{project_id}/artifacts/{artifact_id}")
def get_project_artifact(
    project_id: str,
    artifact_id: str,
    service: ArtifactService = Depends(get_artifact_service),
):
    artifact = service.get_artifact(project_id=project_id, artifact_id=artifact_id)
    return success_response(message="操作成功", data=artifact)
