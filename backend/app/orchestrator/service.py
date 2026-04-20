from app.core.config import Settings
from app.core.database import Database
from app.models.enums import AgentName, AgentStatus
from app.models.records import AgentRuntimeStatusRecord
from app.utils.ids import generate_id
from app.utils.time import now_iso


class OrchestratorService:
    def __init__(self, database: Database, settings: Settings) -> None:
        self.database = database
        self.settings = settings

    def record_event(
        self,
        project_id: str,
        task_id: str | None,
        event_type: str,
        from_role: str,
        to_role: str,
        message: str,
        related_ref: str | None = None,
    ) -> None:
        self.database.execute(
            """
            INSERT INTO events (
                event_id, project_id, task_id, event_type, from_role, to_role,
                message, related_ref, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                generate_id("evt"),
                project_id,
                task_id,
                event_type,
                from_role,
                to_role,
                message,
                related_ref,
                now_iso(),
            ),
        )

    def list_agent_status(self) -> list[AgentRuntimeStatusRecord]:
        timestamp = now_iso()
        return [
            AgentRuntimeStatusRecord(
                agent_id=agent.value,
                agent_name=agent.value,
                status=AgentStatus.IDLE.value,
                current_task_id=None,
                health="healthy",
                last_heartbeat_at=timestamp,
                updated_at=timestamp,
            )
            for agent in (
                AgentName.CLARIFY,
                AgentName.PM,
                AgentName.ARCHITECT,
                AgentName.DEV,
                AgentName.TEST,
                AgentName.ORCHESTRATOR,
            )
        ]
