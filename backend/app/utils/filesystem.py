import json
import shutil
from pathlib import Path
from typing import Any


PROJECT_SUBDIRECTORIES = (
    "metadata",
    "requirements",
    "prd",
    "architecture",
    "development",
    "development/repair_notes",
    "tests",
    "tests/defect_reports",
    "delivery",
    "exports",
)


def ensure_project_structure(projects_root: Path, project_id: str) -> Path:
    project_root = projects_root / project_id
    for subdirectory in PROJECT_SUBDIRECTORIES:
        (project_root / subdirectory).mkdir(parents=True, exist_ok=True)
    return project_root


def write_text_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json_file(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def to_repo_relative_path(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def resolve_repo_path(path: str | Path, repo_root: Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return repo_root / candidate


def read_text_file(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def export_directory_to_zip(source_dir: Path, destination_base: Path) -> Path:
    archive_path = shutil.make_archive(
        base_name=str(destination_base),
        format="zip",
        root_dir=source_dir.parent,
        base_dir=source_dir.name,
    )
    return Path(archive_path)
