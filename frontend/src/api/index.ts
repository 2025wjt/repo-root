import type { Approval, Artifact, Event, OverviewResponse, Task } from "../types";
import { requestData } from "./request";

export interface CreateProjectRequest {
  name: string;
  description?: string;
  raw_requirement: string;
}

export interface CreateProjectResponse {
  project_id: string;
  status: string;
  current_stage: string;
}

export interface SubmitApprovalRequest {
  action: "approved" | "rejected";
  reviewer: string;
  comment: string;
}

export interface ExportProjectResponse {
  project_id: string;
  export_file_name: string;
  export_path: string;
}

export function createProject(payload: CreateProjectRequest) {
  return requestData<CreateProjectResponse>("/projects", {
    method: "POST",
    body: payload,
  });
}

export function getProjectOverview(projectId: string) {
  return requestData<OverviewResponse>(`/projects/${projectId}/overview`);
}

export function getProjectTasks(projectId: string, query?: { stage?: string; status?: string }) {
  return requestData<Task[]>(`/projects/${projectId}/tasks`, { query });
}

export function getTask(taskId: string) {
  return requestData<Task>(`/tasks/${taskId}`);
}

export function getProjectApprovals(projectId: string, query?: { status?: string }) {
  return requestData<Approval[]>(`/projects/${projectId}/approvals`, { query });
}

export function submitApproval(approvalId: string, payload: SubmitApprovalRequest) {
  return requestData<{ approval_id: string; status: string }>(`/approvals/${approvalId}/submit`, {
    method: "POST",
    body: payload,
  });
}

export function getProjectArtifacts(projectId: string, query?: { artifact_type?: string }) {
  return requestData<Artifact[]>(`/projects/${projectId}/artifacts`, { query });
}

export function getArtifact(projectId: string, artifactId: string) {
  return requestData<Artifact & { content: string }>(`/projects/${projectId}/artifacts/${artifactId}`);
}

export function getProjectEvents(projectId: string, query?: { limit?: number }) {
  return requestData<Event[]>(`/projects/${projectId}/events`, { query });
}

export function exportProject(projectId: string) {
  return requestData<ExportProjectResponse>(`/projects/${projectId}/export`, {
    method: "POST",
    body: { export_type: "delivery_bundle" },
  });
}
