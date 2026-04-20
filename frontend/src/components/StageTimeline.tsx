import { StatusBadge } from "./StatusBadge";

export interface StageItem {
  id: string;
  label: string;
  status: "done" | "current" | "pending" | "blocked" | "failed";
  note?: string;
}

interface StageTimelineProps {
  items: StageItem[];
}

function toneForStage(status: StageItem["status"]) {
  switch (status) {
    case "done":
      return "success";
    case "current":
      return "info";
    case "blocked":
    case "failed":
      return "danger";
    default:
      return "neutral";
  }
}

export function StageTimeline({ items }: StageTimelineProps) {
  return (
    <section className="card">
      <div className="card-heading">
        <h2>流程时间线</h2>
        <p>固定 9 节点主链路，后端接入后会驱动状态变化。</p>
      </div>
      <div className="timeline">
        {items.map((item) => (
          <article key={item.id} className={`timeline-item timeline-item--${item.status}`}>
            <div className="timeline-marker" />
            <div className="timeline-content">
              <div className="timeline-head">
                <strong>{item.label}</strong>
                <StatusBadge label={item.status} tone={toneForStage(item.status)} compact />
              </div>
              {item.note ? <p>{item.note}</p> : null}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
