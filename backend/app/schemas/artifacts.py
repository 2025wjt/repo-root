from pydantic import BaseModel


class ArtifactContentResponse(BaseModel):
    artifact_id: str
    artifact_type: str
    artifact_name: str
    uri: str
    content_type: str
    content: str
