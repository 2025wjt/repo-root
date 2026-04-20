from pydantic import BaseModel, Field


class CreateProjectRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    raw_requirement: str = Field(min_length=1)


class ExportProjectRequest(BaseModel):
    export_type: str = "delivery_bundle"
