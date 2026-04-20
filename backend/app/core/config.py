import os
from pathlib import Path

from pydantic import BaseModel, Field

REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseModel):
    app_name: str = "AI Requirement Workflow Engine Backend"
    debug: bool = False
    default_created_by: str = "user"
    repo_root: Path = REPO_ROOT
    database_path: Path = Field(default_factory=lambda: REPO_ROOT / "data" / "app.db")
    data_dir: Path = Field(default_factory=lambda: REPO_ROOT / "data")
    projects_dir: Path = Field(default_factory=lambda: REPO_ROOT / "projects")
    exports_dir: Path = Field(default_factory=lambda: REPO_ROOT / "data" / "exports")

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            app_name=os.getenv("APP_NAME", cls.model_fields["app_name"].default),
            debug=os.getenv("APP_DEBUG", "false").lower() == "true",
            repo_root=Path(
                os.getenv(
                    "APP_REPO_ROOT",
                    cls.model_fields["repo_root"].default,
                )
            ),
            database_path=Path(
                os.getenv(
                    "APP_DATABASE_PATH",
                    cls.model_fields["database_path"].default_factory(),
                )
            ),
            data_dir=Path(
                os.getenv(
                    "APP_DATA_DIR",
                    cls.model_fields["data_dir"].default_factory(),
                )
            ),
            projects_dir=Path(
                os.getenv(
                    "APP_PROJECTS_DIR",
                    cls.model_fields["projects_dir"].default_factory(),
                )
            ),
            exports_dir=Path(
                os.getenv(
                    "APP_EXPORTS_DIR",
                    cls.model_fields["exports_dir"].default_factory(),
                )
            ),
        )


def get_settings() -> Settings:
    return Settings.from_env()
