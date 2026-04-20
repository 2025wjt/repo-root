from pydantic import BaseModel, Field

from app.models.enums import ApprovalAction


class SubmitApprovalRequest(BaseModel):
    action: ApprovalAction
    reviewer: str = Field(min_length=1, max_length=100)
    comment: str | None = Field(default=None, max_length=2000)
