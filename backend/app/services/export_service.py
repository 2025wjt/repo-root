import shutil
from pathlib import Path

from app.core.config import Settings
from app.core.database import Database
from app.utils.exceptions import AppError
from app.utils.filesystem import export_directory_to_zip, to_repo_relative_path


class ExportService:
    def __init__(self, database: Database, settings: Settings) -> None:
        self.database = database
        self.settings = settings

    def export_project(self, project_id: str, export_type: str) -> dict:
        if export_type != "delivery_bundle":
            raise AppError.bad_request(
                "VALIDATION_ERROR",
                "当前仅支持 delivery_bundle 导出类型",
                {"export_type": export_type},
            )

        project = self.database.fetch_one(
            "SELECT project_id FROM projects WHERE project_id = ?",
            (project_id,),
        )
        if project is None:
            raise AppError.not_found("PROJECT_NOT_FOUND", "未找到对应项目", {"project_id": project_id})

        project_dir = Path(self.settings.projects_dir) / project_id
        if not project_dir.exists():
            raise AppError.not_found(
                "EXPORT_FAILED",
                "项目目录不存在，无法导出",
                {"project_id": project_id},
            )

        staged_zip = export_directory_to_zip(
            source_dir=project_dir,
            destination_base=Path(self.settings.exports_dir) / f"{project_id}_delivery_bundle",
        )
        export_dir = project_dir / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)
        zip_path = export_dir / staged_zip.name
        shutil.copyfile(staged_zip, zip_path)
        return {
            "project_id": project_id,
            "export_file_name": zip_path.name,
            "export_path": to_repo_relative_path(zip_path, self.settings.projects_dir.parent),
        }
