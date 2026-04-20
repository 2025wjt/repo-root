from fastapi import Request

from app.core.config import Settings
from app.core.database import Database
from app.services.approval_service import ApprovalService
from app.services.artifact_service import ArtifactService
from app.services.export_service import ExportService
from app.services.project_service import ProjectService
from app.services.task_service import TaskService


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_database(request: Request) -> Database:
    return request.app.state.database


def get_project_service(request: Request) -> ProjectService:
    return ProjectService(
        database=get_database(request),
        settings=get_settings(request),
    )


def get_task_service(request: Request) -> TaskService:
    return TaskService(database=get_database(request))


def get_approval_service(request: Request) -> ApprovalService:
    return ApprovalService(database=get_database(request))


def get_artifact_service(request: Request) -> ArtifactService:
    return ArtifactService(
        database=get_database(request),
        settings=get_settings(request),
    )


def get_export_service(request: Request) -> ExportService:
    return ExportService(
        database=get_database(request),
        settings=get_settings(request),
    )
