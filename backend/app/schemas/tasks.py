from pydantic import BaseModel


class TaskEnvelope(BaseModel):
    task_id: str
    project_id: str
    task_type: str
    assigned_agent: str
    stage: str
    version: int
    input_data: dict
    context: dict
    expected_output: dict
