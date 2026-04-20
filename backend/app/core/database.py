import sqlite3
from contextlib import contextmanager
from typing import Any

from app.core.config import Settings

SCHEMA_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS projects (
        project_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        status TEXT NOT NULL,
        current_stage TEXT NOT NULL,
        current_version INTEGER NOT NULL,
        requirement_summary TEXT NOT NULL,
        created_by TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        completed_at TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS tasks (
        task_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        task_type TEXT NOT NULL,
        task_name TEXT NOT NULL,
        stage TEXT NOT NULL,
        assigned_agent TEXT NOT NULL,
        status TEXT NOT NULL,
        priority TEXT NOT NULL,
        depends_on TEXT NOT NULL,
        input_ref TEXT,
        output_ref TEXT,
        retry_count INTEGER NOT NULL,
        max_retry_count INTEGER NOT NULL,
        version INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        started_at TEXT,
        finished_at TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(project_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS approvals (
        approval_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        task_id TEXT,
        approval_type TEXT NOT NULL,
        stage TEXT NOT NULL,
        target_ref TEXT NOT NULL,
        status TEXT NOT NULL,
        reviewer TEXT,
        comment TEXT,
        created_at TEXT NOT NULL,
        reviewed_at TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(project_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS events (
        event_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        task_id TEXT,
        event_type TEXT NOT NULL,
        from_role TEXT NOT NULL,
        to_role TEXT NOT NULL,
        message TEXT NOT NULL,
        related_ref TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(project_id) REFERENCES projects(project_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS artifacts (
        artifact_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        task_id TEXT,
        artifact_type TEXT NOT NULL,
        artifact_name TEXT NOT NULL,
        uri TEXT NOT NULL,
        version INTEGER NOT NULL,
        generated_by TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(project_id) REFERENCES projects(project_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS agent_runtime_status (
        agent_id TEXT PRIMARY KEY,
        agent_name TEXT NOT NULL,
        status TEXT NOT NULL,
        current_task_id TEXT,
        health TEXT NOT NULL,
        last_heartbeat_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
)


class Database:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def initialize(self) -> None:
        self.settings.data_dir.mkdir(parents=True, exist_ok=True)
        self.settings.projects_dir.mkdir(parents=True, exist_ok=True)
        self.settings.exports_dir.mkdir(parents=True, exist_ok=True)
        self.settings.database_path.parent.mkdir(parents=True, exist_ok=True)

        with self.connection() as conn:
            for statement in SCHEMA_STATEMENTS:
                conn.execute(statement)
            conn.commit()

    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.settings.database_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> None:
        with self.connection() as conn:
            conn.execute(query, params)
            conn.commit()

    def fetch_one(self, query: str, params: tuple[Any, ...] = ()) -> sqlite3.Row | None:
        with self.connection() as conn:
            return conn.execute(query, params).fetchone()

    def fetch_all(self, query: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
        with self.connection() as conn:
            return conn.execute(query, params).fetchall()
