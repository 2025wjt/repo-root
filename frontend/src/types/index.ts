export type ProjectStatus =
  | "created"
  | "clarifying"
  | "prd_generating"
  | "waiting_prd_approval"
  | "designing"
  | "waiting_design_approval"
  | "developing"
  | "testing"
  | "reviewing"
  | "delivering"
  | "done"
  | "failed"
  | "paused";

export type TaskStatus =
  | "pending"
  | "dispatched"
  | "processing"
  | "waiting_approval"
  | "blocked"
  | "waiting_repair"
  | "retrying"
  | "done"
  | "failed"
  | "cancelled";

export type ApprovalStatus = "pending" | "approved" | "rejected" | "expired";

export type AgentStatus = "idle" | "busy" | "waiting_input" | "degraded" | "offline";

export type ArtifactType =
  | "structured_requirement"
  | "prd"
  | "architecture_design"
  | "api_contract"
  | "task_list"
  | "test_report"
  | "delivery_note"
  | "final_summary"
  | string;

export interface Project {
  project_id: string;
  name: string;
  description: string | null;
  status: ProjectStatus;
  current_stage: string;
  current_version: number;
  requirement_summary: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface Task {
  task_id: string;
  project_id: string;
  task_type: string;
  task_name: string;
  stage: string;
  assigned_agent: string;
  status: TaskStatus;
  priority: "low" | "medium" | "high";
  depends_on: string[];
  input_ref: string | null;
  output_ref: string | null;
  retry_count: number;
  max_retry_count: number;
  version: number;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
}

export interface Approval {
  approval_id: string;
  project_id: string;
  task_id: string | null;
  approval_type: string;
  stage: string;
  target_ref: string;
  status: ApprovalStatus;
  reviewer: string | null;
  comment: string | null;
  created_at: string;
  reviewed_at: string | null;
}

export interface Event {
  event_id: string;
  project_id: string;
  task_id: string | null;
  event_type: string;
  from_role: string;
  to_role: string;
  message: string;
  related_ref: string | null;
  created_at: string;
}

export interface Artifact {
  artifact_id: string;
  project_id: string;
  task_id: string | null;
  artifact_type: ArtifactType;
  artifact_name: string;
  uri: string;
  version: number;
  generated_by: string;
  status: "active" | "archived";
  created_at: string;
  content_type?: "markdown" | "json" | "text";
}

export interface AgentRuntimeStatus {
  agent_id: string;
  agent_name: string;
  status: AgentStatus;
  current_task_id: string | null;
  health: "healthy" | "degraded" | "offline";
  last_heartbeat_at: string;
  updated_at: string;
}

export interface ApiSuccess<T> {
  success: true;
  message: string;
  data: T;
}

export interface ApiFailure {
  success: false;
  error_code: string;
  message: string;
  details?: Record<string, unknown>;
}

export type ApiResponse<T> = ApiSuccess<T> | ApiFailure;

export interface OverviewResponse {
  project: Project;
  task_summary: {
    total: number;
    completed: number;
    pending_approval: number;
    repair_count: number;
  };
  approval_summary: {
    total: number;
    pending: number;
    approved: number;
    rejected: number;
  };
  current_focus: string;
  recent_events: Event[];
  agent_statuses: AgentRuntimeStatus[];
}
