from abc import ABC, abstractmethod


class BaseAgent(ABC):
    agent_name: str

    @abstractmethod
    def run(self, task_envelope: dict) -> dict:
        """Return a spec-aligned placeholder agent result."""
