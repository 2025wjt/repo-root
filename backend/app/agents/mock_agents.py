from app.agents.base import BaseAgent


class MockAgent(BaseAgent):
    def __init__(self, agent_name: str) -> None:
        self.agent_name = agent_name

    def run(self, task_envelope: dict) -> dict:
        expected_output = task_envelope.get("expected_output", {})
        artifact_type = expected_output.get("artifact_type", "artifact")
        return {
            "task_id": task_envelope["task_id"],
            "project_id": task_envelope["project_id"],
            "agent": self.agent_name,
            "status": "done",
            "summary": f"{self.agent_name} 已生成占位产物。",
            "artifacts": [
                {
                    "artifact_type": artifact_type,
                    "artifact_name": f"{artifact_type}_v1.md",
                    "artifact_uri": task_envelope.get("context", {}).get("output_dir", ""),
                }
            ],
            "result_data": {"next_hint": "skeleton-only"},
            "errors": [],
        }
