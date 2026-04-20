from __future__ import annotations

import re
from typing import Any

from .db import Database, json_dumps, json_loads
from .models import AgentRuntimeStatus, Approval, Artifact, Event, Project, Task


class Repository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def next_id(self, table: str, field: str, prefix: str) -> str:
        pattern = re.compile(re.escape(prefix) + r'(\d+)$')
        with self.db.connect() as conn:
            rows = conn.execute(f'SELECT {field} FROM {table}').fetchall()
        max_id = 0
        for row in rows:
            value = row[field]
            match = pattern.search(value)
            if match:
                max_id = max(max_id, int(match.group(1)))
        return f'{prefix}{max_id + 1:03d}'

    def insert_project(self, project: Project) -> None:
        with self.db.connect() as conn:
            conn.execute(
                '''
                INSERT INTO projects (project_id, name, description, status, current_stage, current_version,
                requirement_summary, created_by, created_at, updated_at, completed_at)
                VALUES (:project_id, :name, :description, :status, :current_stage, :current_version,
                :requirement_summary, :created_by, :created_at, :updated_at, :completed_at)
                ''',
                project.model_dump(),
            )

    def update_project(self, project_id: str, **updates: Any) -> None:
        if not updates:
            return
        clause = ', '.join(f'{key} = :{key}' for key in updates)
        updates['project_id'] = project_id
        with self.db.connect() as conn:
            conn.execute(f'UPDATE projects SET {clause} WHERE project_id = :project_id', updates)

    def get_project(self, project_id: str) -> dict[str, Any] | None:
        with self.db.connect() as conn:
            return conn.execute('SELECT * FROM projects WHERE project_id = ?', (project_id,)).fetchone()

    def insert_task(self, task: Task) -> None:
        payload = task.model_dump()
        payload['depends_on'] = json_dumps(payload['depends_on'])
        payload['result_json'] = json_dumps(payload['result_json'])
        with self.db.connect() as conn:
            conn.execute(
                '''
                INSERT INTO tasks (task_id, project_id, task_type, task_name, stage, module_name,
                assigned_agent, status, priority, depends_on, input_ref, output_ref, retry_count,
                max_retry_count, version, summary, result_json, created_at, started_at, finished_at)
                VALUES (:task_id, :project_id, :task_type, :task_name, :stage, :module_name,
                :assigned_agent, :status, :priority, :depends_on, :input_ref, :output_ref, :retry_count,
                :max_retry_count, :version, :summary, :result_json, :created_at, :started_at, :finished_at)
                ''',
                payload,
            )

    def update_task(self, task_id: str, **updates: Any) -> None:
        if 'depends_on' in updates:
            updates['depends_on'] = json_dumps(updates['depends_on'])
        if 'result_json' in updates:
            updates['result_json'] = json_dumps(updates['result_json'])
        clause = ', '.join(f'{key} = :{key}' for key in updates)
        updates['task_id'] = task_id
        with self.db.connect() as conn:
            conn.execute(f'UPDATE tasks SET {clause} WHERE task_id = :task_id', updates)

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        with self.db.connect() as conn:
            row = conn.execute('SELECT * FROM tasks WHERE task_id = ?', (task_id,)).fetchone()
        return self._deserialize_task(row)

    def list_tasks(self, project_id: str, stage: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
        query = 'SELECT * FROM tasks WHERE project_id = :project_id'
        params: dict[str, Any] = {'project_id': project_id}
        if stage:
            query += ' AND stage = :stage'
            params['stage'] = stage
        if status:
            query += ' AND status = :status'
            params['status'] = status
        query += ' ORDER BY created_at ASC'
        with self.db.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._deserialize_task(row) for row in rows]

    def insert_approval(self, approval: Approval) -> None:
        with self.db.connect() as conn:
            conn.execute(
                '''
                INSERT INTO approvals (approval_id, project_id, task_id, approval_type, stage, target_ref,
                artifact_id, status, reviewer, comment, created_at, reviewed_at)
                VALUES (:approval_id, :project_id, :task_id, :approval_type, :stage, :target_ref,
                :artifact_id, :status, :reviewer, :comment, :created_at, :reviewed_at)
                ''',
                approval.model_dump(),
            )

    def update_approval(self, approval_id: str, **updates: Any) -> None:
        clause = ', '.join(f'{key} = :{key}' for key in updates)
        updates['approval_id'] = approval_id
        with self.db.connect() as conn:
            conn.execute(f'UPDATE approvals SET {clause} WHERE approval_id = :approval_id', updates)

    def get_approval(self, approval_id: str) -> dict[str, Any] | None:
        with self.db.connect() as conn:
            return conn.execute('SELECT * FROM approvals WHERE approval_id = ?', (approval_id,)).fetchone()

    def list_approvals(self, project_id: str, status: str | None = None) -> list[dict[str, Any]]:
        query = 'SELECT * FROM approvals WHERE project_id = :project_id'
        params: dict[str, Any] = {'project_id': project_id}
        if status:
            query += ' AND status = :status'
            params['status'] = status
        query += ' ORDER BY created_at DESC'
        with self.db.connect() as conn:
            return conn.execute(query, params).fetchall()

    def insert_event(self, event: Event) -> None:
        payload = event.model_dump()
        payload['metadata_json'] = json_dumps(payload['metadata_json'])
        with self.db.connect() as conn:
            conn.execute(
                '''
                INSERT INTO events (event_id, project_id, task_id, event_type, from_role, to_role, message,
                related_ref, metadata_json, created_at)
                VALUES (:event_id, :project_id, :task_id, :event_type, :from_role, :to_role, :message,
                :related_ref, :metadata_json, :created_at)
                ''',
                payload,
            )

    def list_events(self, project_id: str, limit: int | None = None) -> list[dict[str, Any]]:
        query = 'SELECT * FROM events WHERE project_id = :project_id ORDER BY created_at DESC'
        if limit is not None:
            query += f' LIMIT {int(limit)}'
        with self.db.connect() as conn:
            rows = conn.execute(query, {'project_id': project_id}).fetchall()
        return [self._deserialize_event(row) for row in rows]

    def insert_artifact(self, artifact: Artifact) -> None:
        with self.db.connect() as conn:
            conn.execute(
                '''
                INSERT INTO artifacts (artifact_id, project_id, task_id, artifact_type, artifact_name, uri,
                version, generated_by, status, content_type, created_at)
                VALUES (:artifact_id, :project_id, :task_id, :artifact_type, :artifact_name, :uri,
                :version, :generated_by, :status, :content_type, :created_at)
                ''',
                artifact.model_dump(),
            )

    def get_artifact(self, artifact_id: str) -> dict[str, Any] | None:
        with self.db.connect() as conn:
            return conn.execute('SELECT * FROM artifacts WHERE artifact_id = ?', (artifact_id,)).fetchone()

    def list_artifacts(self, project_id: str, artifact_type: str | None = None) -> list[dict[str, Any]]:
        query = 'SELECT * FROM artifacts WHERE project_id = :project_id'
        params: dict[str, Any] = {'project_id': project_id}
        if artifact_type:
            query += ' AND artifact_type = :artifact_type'
            params['artifact_type'] = artifact_type
        query += ' ORDER BY created_at ASC'
        with self.db.connect() as conn:
            return conn.execute(query, params).fetchall()

    def upsert_agent_status(self, status: AgentRuntimeStatus) -> None:
        payload = status.model_dump()
        with self.db.connect() as conn:
            conn.execute(
                '''
                INSERT INTO agent_runtime_status (agent_id, agent_name, status, current_task_id, health, summary,
                last_heartbeat_at, updated_at)
                VALUES (:agent_id, :agent_name, :status, :current_task_id, :health, :summary,
                :last_heartbeat_at, :updated_at)
                ON CONFLICT(agent_id) DO UPDATE SET
                    agent_name=excluded.agent_name,
                    status=excluded.status,
                    current_task_id=excluded.current_task_id,
                    health=excluded.health,
                    summary=excluded.summary,
                    last_heartbeat_at=excluded.last_heartbeat_at,
                    updated_at=excluded.updated_at
                ''',
                payload,
            )

    def list_agent_statuses(self) -> list[dict[str, Any]]:
        with self.db.connect() as conn:
            return conn.execute('SELECT * FROM agent_runtime_status ORDER BY agent_id ASC').fetchall()

    def _deserialize_task(self, row: dict[str, Any] | None) -> dict[str, Any] | None:
        if row is None:
            return None
        row = dict(row)
        row['depends_on'] = json_loads(row['depends_on'], [])
        row['result_json'] = json_loads(row['result_json'], {})
        return row

    def _deserialize_event(self, row: dict[str, Any]) -> dict[str, Any]:
        result = dict(row)
        result['metadata_json'] = json_loads(result['metadata_json'], {})
        return result
