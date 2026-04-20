from pathlib import Path

from app.core.config import Settings
from app.core.database import Database


def test_database_initialization_creates_sqlite_file(tmp_path: Path) -> None:
    settings = Settings(
        app_name="test-app",
        debug=False,
        database_path=tmp_path / "app.db",
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        exports_dir=tmp_path / "exports",
    )
    database = Database(settings=settings)

    database.initialize()

    assert settings.database_path.exists()
