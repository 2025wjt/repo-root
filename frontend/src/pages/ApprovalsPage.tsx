import { useMemo, useState } from "react";
import { StatusBadge } from "../components/StatusBadge";
import type { Approval } from "../types";

const approvals: Approval[] = [
  {
    approval_id: "approval_prd_001",
    project_id: "project_001",
    task_id: "task_prd_001",
    approval_type: "prd_review",
    stage: "waiting_prd_approval",
    target_ref: "projects/project_001/prd/prd_v1.md",
    status: "pending",
    reviewer: "human_reviewer",
    comment: null,
    created_at: "2026-04-20T10:20:00+08:00",
    reviewed_at: null,
  },
  {
    approval_id: "approval_arch_001",
    project_id: "project_001",
    task_id: "task_arch_001",
    approval_type: "design_review",
    stage: "waiting_design_approval",
    target_ref: "projects/project_001/architecture/architecture_design_v1.md",
    status: "approved",
    reviewer: "human_reviewer",
    comment: "方案结构清晰，可进入开发。",
    created_at: "2026-04-20T10:30:00+08:00",
    reviewed_at: "2026-04-20T10:31:00+08:00",
  },
];

function toneForApproval(status: Approval["status"]) {
  switch (status) {
    case "approved":
      return "success" as const;
    case "rejected":
      return "danger" as const;
    case "pending":
      return "warning" as const;
    default:
      return "neutral" as const;
  }
}

export function ApprovalsPage() {
  const [selectedId, setSelectedId] = useState(approvals[0]?.approval_id ?? "");
  const [message, setMessage] = useState("选择一条审批记录查看详情。");

  const selectedApproval = useMemo(
    () => approvals.find((approval) => approval.approval_id === selectedId) ?? approvals[0] ?? null,
    [selectedId],
  );

  return (
    <section className="page">
      <div className="page-header">
        <div>
          <StatusBadge label="审批页" tone="info" />
          <h2 className="page-title">人工门禁与回流控制</h2>
          <p className="page-subtitle">左侧是审批队列，右侧是文档预览和意见入口。</p>
        </div>
      </div>

      <div className="page-grid page-grid--split">
        <aside className="card list-panel">
          <div className="card-heading">
            <h3>审批列表</h3>
            <p>PRD、技术方案、最终评审都从这里进入。</p>
          </div>
          <div className="list-stack">
            {approvals.map((approval) => (
              <button
                key={approval.approval_id}
                type="button"
                className={`approval-item ${selectedApproval?.approval_id === approval.approval_id ? "is-selected" : ""}`}
                onClick={() => {
                  setSelectedId(approval.approval_id);
                  setMessage("审批详情已切换。");
                }}
              >
                <div className="task-title-row">
                  <strong>{approval.approval_type}</strong>
                  <StatusBadge label={approval.status} tone={toneForApproval(approval.status)} compact />
                </div>
                <p>{approval.target_ref}</p>
              </button>
            ))}
          </div>
        </aside>

        <section className="card stack">
          <div className="card-heading card-heading--split">
            <div>
              <h3>审批详情</h3>
              <p>
                后续接入 <code>GET /api/projects/{"{project_id}"}/approvals</code> 和{" "}
                <code>POST /api/approvals/{"{approval_id}"}/submit</code>。
              </p>
            </div>
          </div>

          {selectedApproval ? (
            <>
              <div className="artifact-meta">
                <StatusBadge label={selectedApproval.approval_type} tone="info" compact />
                <span>{selectedApproval.stage}</span>
                <span>{selectedApproval.created_at}</span>
              </div>

              <pre className="artifact-body">{`审批类型: ${selectedApproval.approval_type}
状态: ${selectedApproval.status}
目标文档: ${selectedApproval.target_ref}
审批意见: ${selectedApproval.comment ?? "待填写"}
`}</pre>

              <div className="field">
                <label htmlFor="approval-comment">审批意见</label>
                <textarea
                  id="approval-comment"
                  className="textarea"
                  rows={5}
                  placeholder="后续接入提交接口时在这里填写意见。"
                />
              </div>

              <div className="action-row">
                <button
                  className="button button-secondary"
                  type="button"
                  onClick={() => setMessage("当前仅展示骨架，后续接入真实审批提交。")}
                >
                  驳回
                </button>
                <button
                  className="button button-primary"
                  type="button"
                  onClick={() => setMessage("当前仅展示骨架，后续接入真实审批提交。")}
                >
                  通过
                </button>
              </div>
              <p className="helper-text">{message}</p>
            </>
          ) : (
            <div className="empty-state">暂无审批数据。</div>
          )}
        </section>
      </div>
    </section>
  );
}
