import type { Task } from "../types";
import { StatusBadge, type StatusTone } from "./StatusBadge";

interface TaskListProps {
  tasks: Task[];
}

function toneForTask(status: Task["status"]): StatusTone {
  switch (status) {
    case "done":
      return "success";
    case "processing":
    case "retrying":
      return "info";
    case "waiting_approval":
    case "waiting_repair":
    case "pending":
      return "warning";
    case "failed":
    case "blocked":
      return "danger";
    default:
      return "neutral";
  }
}

export function TaskList({ tasks }: TaskListProps) {
  return (
    <section className="card">
      <div className="card-heading">
        <h2>任务面板</h2>
        <p>展示开发、测试和返修任务的状态流转。</p>
      </div>
      <div className="task-list">
        {tasks.map((task) => (
          <article key={task.task_id} className="task-row">
            <div className="task-main">
              <div className="task-title-row">
                <strong>{task.task_name}</strong>
                <StatusBadge label={task.status} tone={toneForTask(task.status)} compact />
              </div>
              <p>
                {task.task_type} · {task.assigned_agent}
              </p>
            </div>
            <dl className="task-meta">
              <div>
                <dt>阶段</dt>
                <dd>{task.stage}</dd>
              </div>
              <div>
                <dt>重试</dt>
                <dd>
                  {task.retry_count}/{task.max_retry_count}
                </dd>
              </div>
            </dl>
          </article>
        ))}
      </div>
    </section>
  );
}
