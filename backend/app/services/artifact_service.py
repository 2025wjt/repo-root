from app.core.config import Settings
from app.core.database import Database
from app.schemas.artifacts import ArtifactContentResponse
from app.utils.exceptions import AppError
from app.utils.filesystem import read_text_file, resolve_repo_path


class ArtifactService:
    def __init__(self, database: Database, settings: Settings) -> None:
        self.database = database
        self.settings = settings

    def get_artifact(self, project_id: str, artifact_id: str) -> dict:
        row = self.database.fetch_one(
            "SELECT * FROM artifacts WHERE project_id = ? AND artifact_id = ?",
            (project_id, artifact_id),
        )
        if row is None:
            raise AppError.not_found(
                "ARTIFACT_NOT_FOUND",
                "未找到对应产物",
                {"project_id": project_id, "artifact_id": artifact_id},
            )

        artifact = dict(row)
        response = ArtifactContentResponse(
            artifact_id=artifact["artifact_id"],
            artifact_type=artifact["artifact_type"],
            artifact_name=artifact["artifact_name"],
            uri=artifact["uri"],
            content_type=artifact["content_type"],
            content=read_text_file(
                resolve_repo_path(artifact["uri"], self.settings.projects_dir.parent)
            ),
        )
        return response.model_dump()
