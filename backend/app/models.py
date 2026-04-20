from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ApiSuccess(BaseModel):
    success: Literal[True] = True
    message: str
    data: Any


class ApiError(BaseModel):
    success: Literal[False] = False
    error_code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class CreateProjectRequest(BaseModel):
    name: str
    description: str = ''
    raw_requirement: str


class SubmitApprovalRequest(BaseModel):
    action: Literal['approved', 'rejected']
    reviewer: str = 'human_reviewer'
    comment: str = ''


class ExportRequest(BaseModel):
    export_type: str = 'delivery_bundle'


class Project(BaseModel):
    project_id: str
    name: str
    description: str
    status: str
    current_stage: str
    current_version: int
    requirement_summary: str
    created_by: str
    created_at: str
    updated_at: str
    completed_at: str | None = None


class Task(BaseModel):
    task_id: str
    project_id: str
    task_type: str
    task_name: str
    stage: str
    module_name: str | None = None
    assigned_agent: str
    status: str
    priority: str
    depends_on: list[str] = Field(default_factory=list)
    input_ref: str | None = None
    output_ref: str | None = None
    retry_count: int = 0
    max_retry_count: int = 2
    version: int = 1
    summary: str = ''
    result_json: dict[str, Any] = Field(default_factory=dict)
    created_at: str
    started_at: str | None = None
    finished_at: str | None = None


class Approval(BaseModel):
    approval_id: str
    project_id: str
    task_id: str | None = None
    approval_type: str
    stage: str
    target_ref: str
    artifact_id: str | None = None
    status: str
    reviewer: str
    comment: str = ''
    created_at: str
    reviewed_at: str | None = None


class Event(BaseModel):
    event_id: str
    project_id: str
    task_id: str | None = None
    event_type: str
    from_role: str
    to_role: str
    message: str
    related_ref: str | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class Artifact(BaseModel):
    artifact_id: str
    project_id: str
    task_id: str | None = None
    artifact_type: str
    artifact_name: str
    uri: str
    version: int
    generated_by: str
    status: str
    content_type: str = 'markdown'
    created_at: str


class AgentRuntimeStatus(BaseModel):
    agent_id: str
    agent_name: str
    status: str
    current_task_id: str | None = None
    health: str = 'healthy'
    summary: str = ''
    last_heartbeat_at: str | None = None
    updated_at: str
