import { useState } from "react";
import { createProject } from "../api";
import { StatusBadge } from "../components/StatusBadge";

const demoRequirement = `开发一个简单的 Todo Web App，支持：
- 用户登录
- 待办事项新增
- 待办事项删除
- 待办事项修改
- 待办事项完成/未完成状态切换`;

export function RequirementInputPage() {
  const [name, setName] = useState("Todo Web App");
  const [description, setDescription] = useState("比赛版演示项目");
  const [requirement, setRequirement] = useState(demoRequirement);
  const [message, setMessage] = useState("填写需求后接入 POST /api/projects。");
  const [submitting, setSubmitting] = useState(false);

  return (
    <section className="page">
      <div className="page-header">
        <div>
          <StatusBadge label="需求输入页" tone="info" />
          <h2 className="page-title">创建项目并启动流程</h2>
          <p className="page-subtitle">仅保留 MVP 需要的原始需求输入入口。</p>
        </div>
      </div>

      <div className="page-grid page-grid--two">
        <form
          className="card form"
          onSubmit={async (event) => {
            event.preventDefault();
            setSubmitting(true);
            try {
              const result = await createProject({
                name,
                description,
                raw_requirement: requirement,
              });
              setMessage(`项目已创建：${result.project_id}，当前状态 ${result.status}。`);
            } catch (error) {
              const messageText = error instanceof Error ? error.message : "创建项目失败";
              setMessage(`创建失败：${messageText}`);
            } finally {
              setSubmitting(false);
            }
          }}
        >
          <div className="field">
            <label htmlFor="project-name">项目名称</label>
            <input
              id="project-name"
              className="input"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="例如：Todo Web App"
            />
          </div>
          <div className="field">
            <label htmlFor="project-description">项目描述</label>
            <input
              id="project-description"
              className="input"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              placeholder="可选"
            />
          </div>
          <div className="field">
            <label htmlFor="raw-requirement">原始需求</label>
            <textarea
              id="raw-requirement"
              className="textarea"
              rows={10}
              value={requirement}
              onChange={(event) => setRequirement(event.target.value)}
            />
          </div>
          <div className="action-row">
            <button
              className="button button-secondary"
              type="button"
              onClick={() => {
                setName("Todo Web App");
                setDescription("比赛版演示项目");
                setRequirement(demoRequirement);
                setMessage("已填充示例需求。");
              }}
            >
              填充示例
            </button>
            <button className="button button-primary" type="submit">
              {submitting ? "创建中..." : "启动流程"}
            </button>
          </div>
          <p className="helper-text">{message}</p>
        </form>

        <aside className="card stack">
          <div className="card-heading">
            <h3>示例需求</h3>
            <p>后续由后端创建项目后写入原始需求文件。</p>
          </div>
          <pre className="artifact-body">{requirement}</pre>
          <div className="notice">
            <strong>接入点</strong>
            <p>已接入 POST /api/projects</p>
          </div>
        </aside>
      </div>
    </section>
  );
}
