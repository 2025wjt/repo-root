import type { ReactNode } from "react";

export type StatusTone = "neutral" | "info" | "success" | "warning" | "danger";

interface StatusBadgeProps {
  label: ReactNode;
  tone?: StatusTone;
  compact?: boolean;
}

export function StatusBadge({ label, tone = "neutral", compact = false }: StatusBadgeProps) {
  return <span className={`status-badge status-badge--${tone} ${compact ? "is-compact" : ""}`}>{label}</span>;
}
