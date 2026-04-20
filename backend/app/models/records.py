from pydantic import BaseModel


class ProjectRecord(BaseModel):
    project_id: str
    name: str
    description: str | None = None
    status: str
    current_stage: str
    current_version: int
    requirement_summary: str
    created_by: str
    created_at: str
    updated_at: str
    completed_at: str | None = None


class TaskRecord(BaseModel):
    task_id: str
    project_id: str
    task_type: str
    task_name: str
    stage: str
    assigned_agent: str
    status: str
    priority: str
    depends_on: list[str]
    input_ref: str | None = None
    output_ref: str | None = None
    retry_count: int
    max_retry_count: int
    version: int
    created_at: str
    started_at: str | None = None
    finished_at: str | None = None


class ApprovalRecord(BaseModel):
    approval_id: str
    project_id: str
    task_id: str | None = None
    approval_type: str
    stage: str
    target_ref: str
    status: str
    reviewer: str | None = None
    comment: str | None = None
    created_at: str
    reviewed_at: str | None = None


class EventRecord(BaseModel):
    event_id: str
    project_id: str
    task_id: str | None = None
    event_type: str
    from_role: str
    to_role: str
    message: str
    related_ref: str | None = None
    created_at: str


class ArtifactRecord(BaseModel):
    artifact_id: str
    project_id: str
    task_id: str | None = None
    artifact_type: str
    artifact_name: str
    uri: str
    version: int
    generated_by: str
    status: str
    content_type: str
    created_at: str


class AgentRuntimeStatusRecord(BaseModel):
    agent_id: str
    agent_name: str
    status: str
    current_task_id: str | None = None
    health: str
    last_heartbeat_at: str
    updated_at: str
