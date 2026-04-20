import json
from pathlib import Path

from app.core.config import Settings
from app.core.database import Database
from app.models.enums import (
    AgentName,
    ArtifactStatus,
    ArtifactType,
    ProjectStage,
    ProjectStatus,
)
from app.models.records import ArtifactRecord, ApprovalRecord, EventRecord, ProjectRecord, TaskRecord
from app.orchestrator.service import OrchestratorService
from app.schemas.projects import CreateProjectRequest
from app.utils.exceptions import AppError
from app.utils.filesystem import (
    ensure_project_structure,
    to_repo_relative_path,
    write_json_file,
    write_text_file,
)
from app.utils.ids import generate_id
from app.utils.time import now_iso


class ProjectService:
    def __init__(self, database: Database, settings: Settings) -> None:
        self.database = database
        self.settings = settings
        self.orchestrator = OrchestratorService(database=database, settings=settings)

    def create_project(self, payload: CreateProjectRequest) -> ProjectRecord:
        timestamp = now_iso()
        project_id = generate_id("project")
        project = ProjectRecord(
            project_id=project_id,
            name=payload.name,
            description=payload.description,
            status=ProjectStatus.CREATED.value,
            current_stage=ProjectStage.PROJECT_CREATED.value,
            current_version=1,
            requirement_summary=payload.raw_requirement,
            created_by=self.settings.default_created_by,
            created_at=timestamp,
            updated_at=timestamp,
            completed_at=None,
        )

        project_root = ensure_project_structure(Path(self.settings.projects_dir), project_id)
        raw_requirement_path = project_root / "requirements" / "raw_requirement_v1.md"
        metadata_path = project_root / "metadata" / "project_meta.json"
        raw_requirement_uri = to_repo_relative_path(
            raw_requirement_path,
            self.settings.projects_dir.parent,
        )
        write_text_file(raw_requirement_path, payload.raw_requirement)
        write_json_file(metadata_path, project.model_dump())

        self.database.execute(
            """
            INSERT INTO projects (
                project_id, name, description, status, current_stage, current_version,
                requirement_summary, created_by, created_at, updated_at, completed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project.project_id,
                project.name,
                project.description,
                project.status,
                project.current_stage,
                project.current_version,
                project.requirement_summary,
                project.created_by,
                project.created_at,
                project.updated_at,
                project.completed_at,
            ),
        )

        self.database.execute(
            """
            INSERT INTO artifacts (
                artifact_id, project_id, task_id, artifact_type, artifact_name, uri,
                version, generated_by, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                generate_id("artifact"),
                project.project_id,
                None,
                ArtifactType.RAW_REQUIREMENT.value,
                raw_requirement_path.name,
                raw_requirement_uri,
                1,
                AgentName.ORCHESTRATOR.value,
                ArtifactStatus.ACTIVE.value,
                timestamp,
            ),
        )

        self.orchestrator.record_event(
            project_id=project.project_id,
            task_id=None,
            event_type="project_created",
            from_role=AgentName.ORCHESTRATOR.value,
            to_role=AgentName.ORCHESTRATOR.value,
            message="项目已创建，后续流程骨架待推进。",
            related_ref=raw_requirement_uri,
        )
        return project

    def get_project(self, project_id: str) -> ProjectRecord:
        row = self.database.fetch_one(
            "SELECT * FROM projects WHERE project_id = ?",
            (project_id,),
        )
        if row is None:
            raise AppError.not_found("PROJECT_NOT_FOUND", "未找到对应项目", {"project_id": project_id})
        return ProjectRecord(**dict(row))

    def get_overview(self, project_id: str) -> dict:
        project = self.get_project(project_id)
        tasks = self.list_tasks(project_id)
        approvals = self.list_approvals(project_id)
        events = self.list_events(project_id, limit=10)
        agent_status = self.orchestrator.list_agent_status()

        return {
            "project": project.model_dump(),
            "task_summary": {
                "total": len(tasks),
                "completed": sum(1 for task in tasks if task.status == "done"),
                "pending_approval": sum(1 for task in tasks if task.status == "waiting_approval"),
                "repair_count": sum(
                    1 for task in tasks if task.task_type in {"repair_module", "retest_module"}
                ),
            },
            "approval_summary": {
                "total": len(approvals),
                "pending": sum(1 for approval in approvals if approval.status == "pending"),
                "approved": sum(1 for approval in approvals if approval.status == "approved"),
                "rejected": sum(1 for approval in approvals if approval.status == "rejected"),
            },
            "current_focus": "当前为初始骨架阶段，后续将继续接入固定 Pipeline 推进逻辑。",
            "recent_events": [event.model_dump() for event in events],
            "agent_statuses": [status.model_dump() for status in agent_status],
        }

    def list_tasks(
        self,
        project_id: str,
        stage: str | None = None,
        status: str | None = None,
    ) -> list[TaskRecord]:
        self.get_project(project_id)
        query = "SELECT * FROM tasks WHERE project_id = ?"
        params: list[str] = [project_id]

        if stage:
            query += " AND stage = ?"
            params.append(stage)
        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY created_at ASC"
        rows = self.database.fetch_all(query, tuple(params))
        return [self._row_to_task(row) for row in rows]

    def list_approvals(
        self,
        project_id: str,
        status: str | None = None,
    ) -> list[ApprovalRecord]:
        self.get_project(project_id)
        query = "SELECT * FROM approvals WHERE project_id = ?"
        params: list[str] = [project_id]

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC"
        rows = self.database.fetch_all(query, tuple(params))
        return [ApprovalRecord(**dict(row)) for row in rows]

    def list_artifacts(
        self,
        project_id: str,
        artifact_type: str | None = None,
    ) -> list[ArtifactRecord]:
        self.get_project(project_id)
        query = "SELECT * FROM artifacts WHERE project_id = ?"
        params: list[str] = [project_id]

        if artifact_type:
            query += " AND artifact_type = ?"
            params.append(artifact_type)

        query += " ORDER BY created_at DESC"
        rows = self.database.fetch_all(query, tuple(params))
        return [ArtifactRecord(**dict(row)) for row in rows]

    def list_events(self, project_id: str, limit: int = 20) -> list[EventRecord]:
        self.get_project(project_id)
        rows = self.database.fetch_all(
            "SELECT * FROM events WHERE project_id = ? ORDER BY created_at DESC LIMIT ?",
            (project_id, limit),
        )
        return [EventRecord(**dict(row)) for row in rows]

    def _row_to_task(self, row) -> TaskRecord:
        payload = dict(row)
        payload["depends_on"] = json.loads(payload["depends_on"])
        return TaskRecord(**payload)
