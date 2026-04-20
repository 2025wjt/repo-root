from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_approval_service, get_project_service
from app.schemas.approvals import SubmitApprovalRequest
from app.services.approval_service import ApprovalService
from app.services.project_service import ProjectService
from app.utils.responses import success_response

router = APIRouter()


@router.get("/projects/{project_id}/approvals")
def list_project_approvals(
    project_id: str,
    status_filter: str | None = Query(default=None, alias="status"),
    service: ProjectService = Depends(get_project_service),
):
    approvals = service.list_approvals(project_id=project_id, status=status_filter)
    return success_response(
        message="操作成功",
        data=[approval.model_dump() for approval in approvals],
    )


@router.post("/approvals/{approval_id}/submit")
def submit_approval(
    approval_id: str,
    payload: SubmitApprovalRequest,
    service: ApprovalService = Depends(get_approval_service),
):
    approval = service.submit_approval(approval_id=approval_id, payload=payload)
    return success_response(message="审批提交成功", data=approval.model_dump())
