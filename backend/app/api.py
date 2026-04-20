from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from .models import CreateProjectRequest, ExportRequest, SubmitApprovalRequest
from .orchestrator import Orchestrator
from .repository import Repository


def create_router(repo: Repository, orchestrator: Orchestrator) -> APIRouter:
    router = APIRouter(prefix='/api')

    def success(message: str, data: object) -> dict[str, object]:
        return {'success': True, 'message': message, 'data': data}

    def not_found(code: str, message: str, **details: object) -> HTTPException:
        return HTTPException(status_code=404, detail={'success': False, 'error_code': code, 'message': message, 'details': details})

    @router.post('/projects')
    def create_project(payload: CreateProjectRequest) -> dict[str, object]:
        project = orchestrator.create_project(payload.name, payload.description, payload.raw_requirement)
        return success('项目创建成功', {'project_id': project['project_id'], 'status': project['status'], 'current_stage': project['current_stage']})

    @router.get('/projects/{project_id}')
    def get_project(project_id: str) -> dict[str, object]:
        project = repo.get_project(project_id)
        if project is None:
            raise not_found('PROJECT_NOT_FOUND', '未找到对应项目', project_id=project_id)
        return success('查询成功', project)

    @router.get('/projects/{project_id}/overview')
    def get_overview(project_id: str) -> dict[str, object]:
        try:
            overview = orchestrator.overview(project_id)
        except KeyError:
            raise not_found('PROJECT_NOT_FOUND', '未找到对应项目', project_id=project_id)
        return success('查询成功', overview)

    @router.get('/projects/{project_id}/tasks')
    def list_tasks(project_id: str, stage: str | None = Query(default=None), status: str | None = Query(default=None)) -> dict[str, object]:
        if repo.get_project(project_id) is None:
            raise not_found('PROJECT_NOT_FOUND', '未找到对应项目', project_id=project_id)
        return success('查询成功', repo.list_tasks(project_id, stage=stage, status=status))

    @router.get('/tasks/{task_id}')
    def get_task(task_id: str) -> dict[str, object]:
        task = repo.get_task(task_id)
        if task is None:
            raise not_found('TASK_NOT_FOUND', '未找到对应任务', task_id=task_id)
        return success('查询成功', task)

    @router.get('/projects/{project_id}/approvals')
    def list_approvals(project_id: str, status: str | None = Query(default=None)) -> dict[str, object]:
        if repo.get_project(project_id) is None:
            raise not_found('PROJECT_NOT_FOUND', '未找到对应项目', project_id=project_id)
        approvals = repo.list_approvals(project_id, status=status)
        return success('查询成功', approvals)

    @router.post('/approvals/{approval_id}/submit')
    def submit_approval(approval_id: str, payload: SubmitApprovalRequest) -> dict[str, object]:
        try:
            approval = orchestrator.submit_approval(approval_id, payload.action, payload.reviewer, payload.comment)
        except KeyError:
            raise not_found('APPROVAL_NOT_FOUND', '未找到审批记录', approval_id=approval_id)
        except ValueError:
            raise HTTPException(status_code=400, detail={'success': False, 'error_code': 'APPROVAL_ALREADY_PROCESSED', 'message': '审批已处理，不能重复提交', 'details': {'approval_id': approval_id}})
        return success('审批提交成功', approval)

    @router.get('/projects/{project_id}/artifacts')
    def list_artifacts(project_id: str, artifact_type: str | None = Query(default=None)) -> dict[str, object]:
        if repo.get_project(project_id) is None:
            raise not_found('PROJECT_NOT_FOUND', '未找到对应项目', project_id=project_id)
        return success('查询成功', repo.list_artifacts(project_id, artifact_type=artifact_type))

    @router.get('/projects/{project_id}/artifacts/{artifact_id}')
    def get_artifact(project_id: str, artifact_id: str) -> dict[str, object]:
        if repo.get_project(project_id) is None:
            raise not_found('PROJECT_NOT_FOUND', '未找到对应项目', project_id=project_id)
        artifact = repo.get_artifact(artifact_id)
        if artifact is None or artifact['project_id'] != project_id:
            raise not_found('ARTIFACT_NOT_FOUND', '未找到对应产物', artifact_id=artifact_id)
        path = Path(__file__).resolve().parents[2] / artifact['uri']
        if not path.exists():
            raise not_found('ARTIFACT_NOT_FOUND', '产物文件不存在', artifact_id=artifact_id)
        if artifact['content_type'] == 'zip':
            content = f"Binary artifact available at {artifact['uri']}"
        else:
            content = path.read_text(encoding='utf-8')
        return success('查询成功', {'artifact': artifact, 'content': content, 'content_type': artifact['content_type']})

    @router.get('/projects/{project_id}/events')
    def list_events(project_id: str, limit: int = Query(default=20, ge=1, le=100)) -> dict[str, object]:
        if repo.get_project(project_id) is None:
            raise not_found('PROJECT_NOT_FOUND', '未找到对应项目', project_id=project_id)
        return success('查询成功', repo.list_events(project_id, limit=limit))

    @router.post('/projects/{project_id}/export')
    def export_project(project_id: str, payload: ExportRequest) -> dict[str, object]:
        if payload.export_type != 'delivery_bundle':
            raise HTTPException(status_code=400, detail={'success': False, 'error_code': 'EXPORT_FAILED', 'message': '仅支持 delivery_bundle 导出', 'details': {'export_type': payload.export_type}})
        try:
            result = orchestrator.export_project(project_id)
        except KeyError:
            raise not_found('PROJECT_NOT_FOUND', '未找到对应项目', project_id=project_id)
        return success('导出成功', result)

    return router
