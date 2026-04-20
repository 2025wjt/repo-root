from collections.abc import Iterator
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import Settings
from app.main import create_app


@pytest.fixture()
def test_settings(tmp_path) -> Settings:
    return Settings(
        app_name="workflow-engine-test",
        debug=False,
        database_path=tmp_path / "app.db",
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        exports_dir=tmp_path / "exports",
    )


@pytest.fixture()
def client(test_settings: Settings) -> Iterator[TestClient]:
    app = create_app(settings=test_settings)
    with TestClient(app) as test_client:
        yield test_client
