from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from .config import DB_PATH, DATA_DIR


def dict_factory(cursor: sqlite3.Cursor, row: tuple[Any, ...]) -> dict[str, Any]:
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


class Database:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or DB_PATH
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = dict_factory
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def init(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                '''
                CREATE TABLE IF NOT EXISTS projects (
                    project_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL,
                    current_stage TEXT NOT NULL,
                    current_version INTEGER NOT NULL,
                    requirement_summary TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    completed_at TEXT
                );

                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    task_name TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    module_name TEXT,
                    assigned_agent TEXT NOT NULL,
                    status TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    depends_on TEXT NOT NULL,
                    input_ref TEXT,
                    output_ref TEXT,
                    retry_count INTEGER NOT NULL,
                    max_retry_count INTEGER NOT NULL,
                    version INTEGER NOT NULL,
                    summary TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    finished_at TEXT
                );

                CREATE TABLE IF NOT EXISTS approvals (
                    approval_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    task_id TEXT,
                    approval_type TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    target_ref TEXT NOT NULL,
                    artifact_id TEXT,
                    status TEXT NOT NULL,
                    reviewer TEXT NOT NULL,
                    comment TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    reviewed_at TEXT
                );

                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    task_id TEXT,
                    event_type TEXT NOT NULL,
                    from_role TEXT NOT NULL,
                    to_role TEXT NOT NULL,
                    message TEXT NOT NULL,
                    related_ref TEXT,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

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
                    content_type TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS agent_runtime_status (
                    agent_id TEXT PRIMARY KEY,
                    agent_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    current_task_id TEXT,
                    health TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    last_heartbeat_at TEXT,
                    updated_at TEXT NOT NULL
                );
                '''
            )


def json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def json_loads(value: str | None, default: Any) -> Any:
    if not value:
        return default
    return json.loads(value)
