import { StatusBadge } from "../components/StatusBadge";
import { StageTimeline, type StageItem } from "../components/StageTimeline";
import { TaskList } from "../components/TaskList";
import { EventFeed } from "../components/EventFeed";
import type { Event, Task } from "../types";

const stageItems: StageItem[] = [
  { id: "1", label: "需求提交", status: "done", note: "原始需求已接收" },
  { id: "2", label: "需求澄清", status: "done", note: "结构化需求已生成" },
  { id: "3", label: "PRD 生成", status: "done", note: "文档待审批" },
  { id: "4", label: "PRD 审批", status: "current", note: "等待人工门禁" },
  { id: "5", label: "技术方案", status: "pending" },
  { id: "6", label: "技术方案审批", status: "pending" },
  { id: "7", label: "开发执行", status: "pending" },
  { id: "8", label: "测试验证", status: "pending" },
  { id: "9", label: "最终评审", status: "pending" },
];

const tasks: Task[] = [
  {
    task_id: "task_dev_login_001",
    project_id: "project_001",
    task_type: "implement_module",
    task_name: "用户登录模块",
    stage: "development",
    assigned_agent: "dev",
    status: "waiting_repair",
    priority: "high",
    depends_on: [],
    input_ref: null,
    output_ref: "projects/project_001/development/login_impl_v1.md",
    retry_count: 1,
    max_retry_count: 2,
    version: 1,
    created_at: "2026-04-20T10:00:00+08:00",
    started_at: "2026-04-20T10:05:00+08:00",
    finished_at: null,
  },
  {
    task_id: "task_test_login_001",
    project_id: "project_001",
    task_type: "test_module",
    task_name: "用户登录测试",
    stage: "testing",
    assigned_agent: "test",
    status: "processing",
    priority: "high",
    depends_on: ["task_dev_login_001"],
    input_ref: "projects/project_001/development/login_impl_v1.md",
    output_ref: null,
    retry_count: 0,
    max_retry_count: 2,
    version: 1,
    created_at: "2026-04-20T10:12:00+08:00",
    started_at: "2026-04-20T10:13:00+08:00",
    finished_at: null,
  },
  {
    task_id: "task_dev_todo_001",
    project_id: "project_001",
    task_type: "implement_module",
    task_name: "Todo CRUD 模块",
    stage: "development",
    assigned_agent: "dev",
    status: "done",
    priority: "high",
    depends_on: [],
    input_ref: null,
    output_ref: "projects/project_001/development/todo_impl_v1.md",
    retry_count: 0,
    max_retry_count: 2,
    version: 1,
    created_at: "2026-04-20T09:55:00+08:00",
    started_at: "2026-04-20T10:00:00+08:00",
    finished_at: "2026-04-20T10:18:00+08:00",
  },
];

const events: Event[] = [
  {
    event_id: "evt_005",
    project_id: "project_001",
    task_id: "task_test_login_001",
    event_type: "test_started",
    from_role: "test",
    to_role: "orchestrator",
    message: "登录模块测试已启动",
    related_ref: "projects/project_001/tests/test_report_login_v1.md",
    created_at: "2026-04-20T10:13:00+08:00",
  },
  {
    event_id: "evt_004",
    project_id: "project_001",
    task_id: "task_dev_login_001",
    event_type: "repair_requested",
    from_role: "test",
    to_role: "dev",
    message: "测试失败，已生成返修任务",
    related_ref: "projects/project_001/development/repair_notes/login_v1.md",
    created_at: "2026-04-20T10:11:00+08:00",
  },
  {
    event_id: "evt_003",
    project_id: "project_001",
    task_id: "task_dev_todo_001",
    event_type: "task_completed",
    from_role: "dev",
    to_role: "orchestrator",
    message: "Todo CRUD 模块实现完成",
    related_ref: "projects/project_001/development/todo_impl_v1.md",
    created_at: "2026-04-20T10:09:00+08:00",
  },
];

export function DashboardPage() {
  return (
    <section className="page">
      <div className="page-header">
        <div>
          <StatusBadge label="流程看板页" tone="info" />
          <h2 className="page-title">展示当前阶段、审批门和返修循环</h2>
          <p className="page-subtitle">重点保留“当前在做什么”和“下一步为何停住”。</p>
        </div>
        <div className="metric-grid metric-grid--inline">
          <div className="metric-card">
            <span className="metric-label">当前状态</span>
            <strong className="metric-value">waiting_prd_approval</strong>
          </div>
          <div className="metric-card">
            <span className="metric-label">当前阶段</span>
            <strong className="metric-value">方案确认前</strong>
          </div>
        </div>
      </div>

      <div className="metric-grid">
        <div className="metric-card">
          <span className="metric-label">任务总数</span>
          <strong className="metric-value">12</strong>
        </div>
        <div className="metric-card">
          <span className="metric-label">已完成任务</span>
          <strong className="metric-value">7</strong>
        </div>
        <div className="metric-card">
          <span className="metric-label">待审批</span>
          <strong className="metric-value">2</strong>
        </div>
        <div className="metric-card">
          <span className="metric-label">返修中</span>
          <strong className="metric-value">1</strong>
        </div>
      </div>

      <div className="notice notice--focus">
        <strong>当前焦点</strong>
        <p>当前等待人工处理：PRD 审批。审批通过后才会进入技术方案阶段。</p>
      </div>

      <StageTimeline items={stageItems} />

      <div className="page-grid page-grid--two">
        <TaskList tasks={tasks} />
        <EventFeed events={events} />
      </div>
    </section>
  );
}
