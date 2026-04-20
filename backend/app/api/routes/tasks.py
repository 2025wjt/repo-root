from fastapi import APIRouter, Depends

from app.api.dependencies import get_task_service
from app.services.task_service import TaskService
from app.utils.responses import success_response

router = APIRouter()


@router.get("/tasks/{task_id}")
def get_task(
    task_id: str,
    service: TaskService = Depends(get_task_service),
):
    task = service.get_task(task_id)
    return success_response(message="操作成功", data=task.model_dump())
