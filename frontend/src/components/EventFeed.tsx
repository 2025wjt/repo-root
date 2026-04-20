import type { Event } from "../types";
import { StatusBadge } from "./StatusBadge";

interface EventFeedProps {
  events: Event[];
}

export function EventFeed({ events }: EventFeedProps) {
  return (
    <section className="card">
      <div className="card-heading">
        <h2>最近事件</h2>
        <p>关键事件按时间倒序显示，用于演示流程推进和回流。</p>
      </div>
      <div className="event-feed">
        {events.map((event) => (
          <article key={event.event_id} className="event-row">
            <div className="event-topline">
              <StatusBadge label={event.event_type} tone="neutral" compact />
              <time>{event.created_at}</time>
            </div>
            <p>{event.message}</p>
            <small>
              {event.from_role} → {event.to_role}
            </small>
          </article>
        ))}
      </div>
    </section>
  );
}
