from app.core.database import Database
from app.models.enums import ApprovalAction, ApprovalStatus, ProjectStage, ProjectStatus
from app.models.records import ApprovalRecord
from app.utils.exceptions import AppError
from app.utils.ids import generate_id
from app.utils.time import now_iso


class ApprovalService:
    def __init__(self, database: Database) -> None:
        self.database = database

    def submit_approval(self, approval_id: str, payload) -> ApprovalRecord:
        row = self.database.fetch_one(
            "SELECT * FROM approvals WHERE approval_id = ?",
            (approval_id,),
        )
        if row is None:
            raise AppError.not_found(
                "APPROVAL_NOT_FOUND",
                "未找到对应审批记录",
                {"approval_id": approval_id},
            )

        approval = ApprovalRecord(**dict(row))
        if approval.status != ApprovalStatus.PENDING.value:
            raise AppError.conflict(
                "APPROVAL_ALREADY_PROCESSED",
                "审批已处理，不能重复提交",
                {"approval_id": approval_id},
            )

        reviewed_at = now_iso()
        next_status = ApprovalStatus.APPROVED.value
        if payload.action == ApprovalAction.REJECTED:
            next_status = ApprovalStatus.REJECTED.value

        self.database.execute(
            """
            UPDATE approvals
            SET status = ?, reviewer = ?, comment = ?, reviewed_at = ?
            WHERE approval_id = ?
            """,
            (
                next_status,
                payload.reviewer,
                payload.comment,
                reviewed_at,
                approval_id,
            ),
        )

        project_status, project_stage = self._next_project_position(
            approval_type=approval.approval_type,
            action=payload.action,
        )
        self.database.execute(
            "UPDATE projects SET status = ?, current_stage = ?, updated_at = ? WHERE project_id = ?",
            (project_status, project_stage, reviewed_at, approval.project_id),
        )
        self.database.execute(
            """
            INSERT INTO events (
                event_id, project_id, task_id, event_type, from_role, to_role, message, related_ref, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                generate_id("evt"),
                approval.project_id,
                approval.task_id,
                "approval_submitted",
                payload.reviewer,
                "orchestrator",
                f"{approval.approval_type} {next_status}",
                approval.target_ref,
                reviewed_at,
            ),
        )

        refreshed = self.database.fetch_one(
            "SELECT * FROM approvals WHERE approval_id = ?",
            (approval_id,),
        )
        return ApprovalRecord(**dict(refreshed))

    def _next_project_position(self, approval_type: str, action: ApprovalAction) -> tuple[str, str]:
        if approval_type == "prd_review":
            if action == ApprovalAction.APPROVED:
                return ProjectStatus.DESIGNING.value, ProjectStage.ARCHITECTURE_GENERATION.value
            return ProjectStatus.PRD_GENERATING.value, ProjectStage.PRD_GENERATION.value

        if approval_type == "design_review":
            if action == ApprovalAction.APPROVED:
                return ProjectStatus.DEVELOPING.value, ProjectStage.DEVELOPMENT_TESTING.value
            return ProjectStatus.DESIGNING.value, ProjectStage.ARCHITECTURE_GENERATION.value

        if approval_type == "final_review":
            if action == ApprovalAction.APPROVED:
                return ProjectStatus.DONE.value, ProjectStage.DELIVERY_COMPLETION.value
            return ProjectStatus.DEVELOPING.value, ProjectStage.DEVELOPMENT_TESTING.value

        raise AppError.bad_request(
            "INVALID_APPROVAL_ACTION",
            "无法识别的审批类型",
            {"approval_type": approval_type},
        )
