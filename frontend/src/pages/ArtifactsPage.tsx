import { useMemo, useState } from "react";
import { StatusBadge } from "../components/StatusBadge";
import { ArtifactViewer } from "../components/ArtifactViewer";
import type { Artifact } from "../types";

const artifacts: Artifact[] = [
  {
    artifact_id: "artifact_req_v1",
    project_id: "project_001",
    task_id: "task_clarify_001",
    artifact_type: "structured_requirement",
    artifact_name: "structured_requirement_v1.md",
    uri: "projects/project_001/requirements/structured_requirement_v1.md",
    version: 1,
    generated_by: "clarify",
    status: "active",
    created_at: "2026-04-20T09:40:00+08:00",
    content_type: "markdown",
  },
  {
    artifact_id: "artifact_prd_v1",
    project_id: "project_001",
    task_id: "task_prd_001",
    artifact_type: "prd",
    artifact_name: "prd_v1.md",
    uri: "projects/project_001/prd/prd_v1.md",
    version: 1,
    generated_by: "pm",
    status: "active",
    created_at: "2026-04-20T10:20:00+08:00",
    content_type: "markdown",
  },
  {
    artifact_id: "artifact_task_list_v1",
    project_id: "project_001",
    task_id: "task_arch_001",
    artifact_type: "task_list",
    artifact_name: "task_list_v1.json",
    uri: "projects/project_001/architecture/task_list_v1.json",
    version: 1,
    generated_by: "architect",
    status: "active",
    created_at: "2026-04-20T10:35:00+08:00",
    content_type: "json",
  },
];

const artifactBodies: Record<string, string> = {
  structured_requirement: `# structured_requirement_v1

{
  "goal": "开发一个 Todo Web App",
  "features": ["登录", "待办新增", "待办删除", "待办修改", "完成状态切换"],
  "constraints": ["比赛版 MVP", "固定流程"]
}`,
  prd: `# prd_v1

## 目标
把用户原始需求转成可审批的产品文档。

## 验收
- 支持登录
- 支持 Todo CRUD
- 支持状态切换`,
  task_list: `[
  {
    "task_id": "task_dev_login_001",
    "task_type": "implement_module",
    "task_name": "用户登录模块"
  },
  {
    "task_id": "task_dev_todo_001",
    "task_type": "implement_module",
    "task_name": "Todo CRUD 模块"
  }
]`,
};

export function ArtifactsPage() {
  const [selectedId, setSelectedId] = useState(artifacts[0]?.artifact_id ?? "");
  const [message, setMessage] = useState("选择一个产物查看内容。");

  const selectedArtifact = useMemo(
    () => artifacts.find((artifact) => artifact.artifact_id === selectedId) ?? artifacts[0] ?? null,
    [selectedId],
  );

  const content = selectedArtifact ? artifactBodies[selectedArtifact.artifact_type] ?? "内容将在后续接入文件读取。" : "";

  return (
    <section className="page">
      <div className="page-header">
        <div>
          <StatusBadge label="产物页" tone="info" />
          <h2 className="page-title">查看流程产物与导出入口</h2>
          <p className="page-subtitle">左侧是产物目录，右侧是内容预览和导出触发位。</p>
        </div>
        <button
          className="button button-primary"
          type="button"
          onClick={() => setMessage("导出接口待后端接入：POST /api/projects/{project_id}/export")}
        >
          导出交付包
        </button>
      </div>

      <div className="page-grid page-grid--split">
        <aside className="card list-panel">
          <div className="card-heading">
            <h3>产物列表</h3>
            <p>需求、PRD、技术方案、任务清单等都将沉淀到这里。</p>
          </div>
          <div className="list-stack">
            {artifacts.map((artifact) => (
              <button
                key={artifact.artifact_id}
                type="button"
                className={`approval-item ${selectedArtifact?.artifact_id === artifact.artifact_id ? "is-selected" : ""}`}
                onClick={() => {
                  setSelectedId(artifact.artifact_id);
                  setMessage("产物内容已切换。");
                }}
              >
                <div className="task-title-row">
                  <strong>{artifact.artifact_name}</strong>
                  <StatusBadge label={artifact.artifact_type} tone="info" compact />
                </div>
                <p>{artifact.uri}</p>
              </button>
            ))}
          </div>
        </aside>

        <ArtifactViewer artifact={selectedArtifact} content={content} />
      </div>

      <p className="helper-text">{message}</p>
    </section>
  );
}
