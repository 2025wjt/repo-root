import json

from app.core.database import Database
from app.models.records import TaskRecord
from app.utils.exceptions import AppError


class TaskService:
    def __init__(self, database: Database) -> None:
        self.database = database

    def get_task(self, task_id: str) -> TaskRecord:
        row = self.database.fetch_one(
            "SELECT * FROM tasks WHERE task_id = ?",
            (task_id,),
        )
        if row is None:
            raise AppError.not_found("TASK_NOT_FOUND", "未找到对应任务", {"task_id": task_id})

        payload = dict(row)
        payload["depends_on"] = json.loads(payload["depends_on"])
        return TaskRecord(**payload)
