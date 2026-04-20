from pathlib import Path

from app.core.config import Settings


def test_create_project_persists_control_and_artifact_data(
    client,
    test_settings: Settings,
) -> None:
    response = client.post(
        "/api/projects",
        json={
            "name": "Todo Web App",
            "description": "Demo project",
            "raw_requirement": "Build a Todo Web App with login and todo CRUD.",
        },
    )

    payload = response.json()

    assert response.status_code == 201
    assert payload["success"] is True
    assert payload["data"]["status"] == "created"

    project_id = payload["data"]["project_id"]
    project_dir = Path(test_settings.projects_dir) / project_id
    assert (project_dir / "requirements" / "raw_requirement_v1.md").exists()

    artifacts_response = client.get(f"/api/projects/{project_id}/artifacts")
    artifacts_payload = artifacts_response.json()
    assert artifacts_response.status_code == 200
    assert artifacts_payload["success"] is True
    assert artifacts_payload["data"][0]["uri"] == f"projects/{project_id}/requirements/raw_requirement_v1.md"
