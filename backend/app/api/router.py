from fastapi import APIRouter

from app.api.routes.approvals import router as approvals_router
from app.api.routes.artifacts import router as artifacts_router
from app.api.routes.events import router as events_router
from app.api.routes.exports import router as exports_router
from app.api.routes.health import router as health_router
from app.api.routes.projects import router as projects_router
from app.api.routes.tasks import router as tasks_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(projects_router, prefix="/api", tags=["projects"])
api_router.include_router(tasks_router, prefix="/api", tags=["tasks"])
api_router.include_router(approvals_router, prefix="/api", tags=["approvals"])
api_router.include_router(artifacts_router, prefix="/api", tags=["artifacts"])
api_router.include_router(events_router, prefix="/api", tags=["events"])
api_router.include_router(exports_router, prefix="/api", tags=["exports"])
