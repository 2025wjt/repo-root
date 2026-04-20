from __future__ import annotations

import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .config import DEFAULT_CREATED_BY, DEFAULT_REVIEWER, EXPORTS_DIR, PROJECTS_DIR
from .models import AgentRuntimeStatus, Approval, Artifact, Event, Project, Task
from .repository import Repository
from .templates import (
    api_contract_markdown,
    architecture_markdown,
    defect_markdown,
    delivery_note,
    final_summary,
    module_impl_markdown,
    prd_markdown,
    structured_requirement_json,
    structured_requirement_markdown,
    task_list_json,
    test_report_markdown,
)


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')


class Orchestrator:
    AGENTS = {
        'clarify': 'Clarify Agent',
        'pm': 'PM Agent',
        'architect': 'Architect Agent',
        'dev': 'Dev Agent',
        'test': 'Test Agent',
        'orchestrator': 'Orchestrator',
    }

    def __init__(self, repo: Repository) -> None:
        self.repo = repo
        self._bootstrap_agent_statuses()

    def create_project(self, name: str, description: str, raw_requirement: str) -> dict[str, Any]:
        project_id = self.repo.next_id('projects', 'project_id', 'project_')
        created_at = now_iso()
        project = Project(
            project_id=project_id,
            name=name,
            description=description,
            status='created',
            current_stage='project_created',
            current_version=1,
            requirement_summary=raw_requirement.strip(),
            created_by=DEFAULT_CREATED_BY,
            created_at=created_at,
            updated_at=created_at,
            completed_at=None,
        )
        self.repo.insert_project(project)
        self._ensure_project_dirs(project_id)
        self._write_project_meta(project_id)
        raw_uri = self._write_text(project_id, 'requirements/raw_requirement_v1.md', raw_requirement.strip() + '\n')
        self._create_artifact(project_id, None, 'raw_requirement', 'raw_requirement_v1.md', raw_uri, 1, 'user')
        self._event(project_id, None, 'project_created', 'user', 'orchestrator', '项目已创建并保存原始需求', raw_uri)
        self._update_project(project_id, status='clarifying', current_stage='requirement_alignment')
        self._run_clarify(project_id)
        self._run_prd(project_id)
        return self.repo.get_project(project_id) or {}

    def submit_approval(self, approval_id: str, action: str, reviewer: str, comment: str) -> dict[str, Any]:
        approval = self.repo.get_approval(approval_id)
        if approval is None:
            raise KeyError('APPROVAL_NOT_FOUND')
        if approval['status'] != 'pending':
            raise ValueError('APPROVAL_ALREADY_PROCESSED')
        reviewed_at = now_iso()
        self.repo.update_approval(
            approval_id,
            status='approved' if action == 'approved' else 'rejected',
            reviewer=reviewer,
            comment=comment,
            reviewed_at=reviewed_at,
        )
        project_id = approval['project_id']
        self._event(
            project_id,
            approval.get('task_id'),
            'approval_submitted',
            reviewer,
            'orchestrator',
            f"{approval['approval_type']} 已{ '通过' if action == 'approved' else '驳回' }",
            approval['target_ref'],
            {'comment': comment, 'action': action},
        )
        if approval['approval_type'] == 'prd_review':
            if action == 'approved':
                self._run_architecture(project_id)
            else:
                self._run_prd(project_id, revision_note=comment or '根据评审意见修订 PRD。')
        elif approval['approval_type'] == 'architecture_review':
            if action == 'approved':
                self._run_dev_test(project_id)
            else:
                self._run_architecture(project_id, revision_note=comment or '根据评审意见修订技术方案。')
        elif approval['approval_type'] == 'final_review':
            if action == 'approved':
                self._complete_project(project_id, comment)
            else:
                self._update_project(project_id, status='developing', current_stage='development_testing')
                self._event(project_id, None, 'review_rejected', reviewer, 'orchestrator', '最终评审驳回，返回开发测试阶段', approval['target_ref'])
        return self.repo.get_approval(approval_id) or {}

    def export_project(self, project_id: str) -> dict[str, Any]:
        project = self.repo.get_project(project_id)
        if project is None:
            raise KeyError('PROJECT_NOT_FOUND')
        project_root = PROJECTS_DIR / project_id
        export_name = f'{project_id}_delivery_bundle.zip'
        export_rel = f'projects/{project_id}/exports/{export_name}'
        bundle_root = project_root / 'exports' / export_name
        if bundle_root.exists():
            bundle_root.unlink()
        tmp_root = project_root / f'{project_id}_delivery_bundle'
        if tmp_root.exists():
            shutil.rmtree(tmp_root)
        tmp_root.mkdir(parents=True, exist_ok=True)
        (tmp_root / '01_requirements').mkdir()
        (tmp_root / '02_prd').mkdir()
        (tmp_root / '03_architecture').mkdir()
        (tmp_root / '04_tasks').mkdir()
        (tmp_root / '05_development').mkdir()
        (tmp_root / '06_tests').mkdir()
        (tmp_root / '07_delivery').mkdir()
        (tmp_root / '08_metadata').mkdir()

        readme = f"# {project_id} Delivery Bundle\n\n本导出包来自 AI 驱动的需求交付流程引擎比赛版 MVP。\n"
        (tmp_root / 'README.md').write_text(readme, encoding='utf-8')

        copy_pairs = [
            ('requirements/structured_requirement_v1.md', '01_requirements/structured_requirement_v1.md'),
            ('requirements/structured_requirement_v1.json', '01_requirements/structured_requirement_v1.json'),
            ('prd/prd_v1.md', '02_prd/prd_v1.md'),
            ('architecture/architecture_design_v1.md', '03_architecture/architecture_design_v1.md'),
            ('architecture/api_contract_v1.md', '03_architecture/api_contract_v1.md'),
            ('architecture/task_list_v1.json', '04_tasks/task_list_v1.json'),
            ('development/login_impl_v1.md', '05_development/login_impl_v1.md'),
            ('development/todo_impl_v1.md', '05_development/todo_impl_v1.md'),
            ('development/repair_notes/login_repair_v2.md', '05_development/login_repair_v2.md'),
            ('tests/login_test_report_v1.md', '06_tests/login_test_report_v1.md'),
            ('tests/login_test_report_v2.md', '06_tests/login_test_report_v2.md'),
            ('tests/todo_test_report_v1.md', '06_tests/todo_test_report_v1.md'),
            ('tests/defect_reports/login_defect_v1.md', '06_tests/login_defect_v1.md'),
            ('delivery/delivery_note_v1.md', '07_delivery/delivery_note_v1.md'),
            ('delivery/final_summary_v1.md', '07_delivery/final_summary_v1.md'),
            ('metadata/project_meta.json', '08_metadata/project_meta.json'),
        ]
        for src_rel, dst_rel in copy_pairs:
            src = project_root / src_rel
            if src.exists():
                dst = tmp_root / dst_rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

        with zipfile.ZipFile(bundle_root, 'w', zipfile.ZIP_DEFLATED) as zf:
            for path in tmp_root.rglob('*'):
                if path.is_file():
                    zf.write(path, arcname=f'{project_id}_delivery_bundle/{path.relative_to(tmp_root).as_posix()}')
        tmp_copy = EXPORTS_DIR / export_name
        shutil.copy2(bundle_root, tmp_copy)
        self._create_artifact(project_id, None, 'export_bundle', export_name, export_rel, 1, 'orchestrator', content_type='zip')
        self._event(project_id, None, 'export_created', 'orchestrator', 'user', '已生成交付 zip 包', export_rel)
        return {
            'project_id': project_id,
            'export_file_name': export_name,
            'export_path': export_rel,
        }

    def overview(self, project_id: str) -> dict[str, Any]:
        project = self.repo.get_project(project_id)
        if project is None:
            raise KeyError('PROJECT_NOT_FOUND')
        tasks = self.repo.list_tasks(project_id)
        approvals = self.repo.list_approvals(project_id)
        events = self.repo.list_events(project_id, limit=15)
        artifacts = self.repo.list_artifacts(project_id)
        agents = self.repo.list_agent_statuses()
        pending_approvals = [item for item in approvals if item['status'] == 'pending']
        failed_or_repair = [item for item in tasks if item['status'] in {'failed', 'waiting_repair', 'retrying'} or item['task_type'] in {'repair_module', 'retest_module'}]
        return {
            'project': project,
            'stats': {
                'task_total': len(tasks),
                'task_done': len([item for item in tasks if item['status'] == 'done']),
                'pending_approvals': len(pending_approvals),
                'repair_related': len(failed_or_repair),
                'artifact_total': len(artifacts),
            },
            'current_focus': self._current_focus(project, pending_approvals, tasks),
            'timeline': self._timeline(project, approvals, tasks),
            'recent_events': events,
            'agent_statuses': agents,
        }

    def _run_clarify(self, project_id: str) -> None:
        project = self._require_project(project_id)
        task = self._create_task(project_id, 'clarify_requirement', '生成结构化需求单', 'requirement_alignment', 'clarify', None, 'high', [])
        self._agent_busy('clarify', task['task_id'], '正在生成结构化需求单')
        md_rel = self._write_text(project_id, 'requirements/structured_requirement_v1.md', structured_requirement_markdown(project['name'], project['requirement_summary']))
        json_rel = self._write_text(project_id, 'requirements/structured_requirement_v1.json', structured_requirement_json(project['name'], project['requirement_summary']))
        self._create_artifact(project_id, task['task_id'], 'structured_requirement', 'structured_requirement_v1.md', md_rel, 1, 'clarify')
        self._create_artifact(project_id, task['task_id'], 'structured_requirement_json', 'structured_requirement_v1.json', json_rel, 1, 'clarify', content_type='json')
        self._finish_task(task['task_id'], '已完成结构化需求单输出', {'next_hint': '生成 PRD'})
        self._event(project_id, task['task_id'], 'task_completed', 'clarify', 'orchestrator', 'Clarify Agent 已完成结构化需求输出', md_rel)
        self._agent_idle('clarify', '结构化需求已完成')
        self._update_project(project_id, status='prd_generating', current_stage='prd_generation')

    def _run_prd(self, project_id: str, revision_note: str = '') -> None:
        project = self._require_project(project_id)
        task_type = 'revise_prd' if revision_note else 'generate_prd'
        task_name = '修订 PRD' if revision_note else '生成 PRD'
        version = self._next_version(project_id, 'prd')
        task = self._create_task(project_id, task_type, task_name, 'prd_generation', 'pm', None, 'high', [])
        self._agent_busy('pm', task['task_id'], '正在生成 PRD')
        prd_name = f'prd_v{version}.md'
        prd_rel = self._write_text(project_id, f'prd/{prd_name}', prd_markdown(project['name'], project['requirement_summary'], revision_note))
        artifact = self._create_artifact(project_id, task['task_id'], 'prd', prd_name, prd_rel, version, 'pm')
        self._finish_task(task['task_id'], '已完成 PRD 生成', {'next_hint': '等待 PRD 审批'})
        self._event(project_id, task['task_id'], 'task_completed', 'pm', 'orchestrator', 'PM Agent 已完成 PRD 生成', prd_rel)
        self._agent_idle('pm', 'PRD 已生成')
        approval_id = self.repo.next_id('approvals', 'approval_id', 'approval_')
        approval = Approval(
            approval_id=approval_id,
            project_id=project_id,
            task_id=task['task_id'],
            approval_type='prd_review',
            stage='waiting_prd_approval',
            target_ref=prd_rel,
            artifact_id=artifact['artifact_id'],
            status='pending',
            reviewer=DEFAULT_REVIEWER,
            comment='',
            created_at=now_iso(),
            reviewed_at=None,
        )
        self.repo.insert_approval(approval)
        self._event(project_id, task['task_id'], 'approval_created', 'orchestrator', DEFAULT_REVIEWER, '已创建 PRD 审批记录', prd_rel)
        self._update_project(project_id, status='waiting_prd_approval', current_stage='waiting_prd_approval')

    def _run_architecture(self, project_id: str, revision_note: str = '') -> None:
        project = self._require_project(project_id)
        version = self._next_version(project_id, 'architecture_design')
        task_type = 'revise_architecture' if revision_note else 'generate_architecture'
        task_name = '修订技术方案' if revision_note else '生成技术方案'
        task = self._create_task(project_id, task_type, task_name, 'architecture_design', 'architect', None, 'high', [])
        self._agent_busy('architect', task['task_id'], '正在生成技术方案和任务清单')
        design_rel = self._write_text(project_id, f'architecture/architecture_design_v{version}.md', architecture_markdown(project['name'], revision_note))
        api_rel = self._write_text(project_id, f'architecture/api_contract_v{version}.md', api_contract_markdown())
        task_rel = self._write_text(project_id, f'architecture/task_list_v{version}.json', task_list_json(project_id))
        design_artifact = self._create_artifact(project_id, task['task_id'], 'architecture_design', f'architecture_design_v{version}.md', design_rel, version, 'architect')
        self._create_artifact(project_id, task['task_id'], 'api_contract', f'api_contract_v{version}.md', api_rel, version, 'architect')
        self._create_artifact(project_id, task['task_id'], 'task_list', f'task_list_v{version}.json', task_rel, version, 'architect', content_type='json')
        self._finish_task(task['task_id'], '已完成技术方案输出', {'next_hint': '等待技术方案审批'})
        self._event(project_id, task['task_id'], 'task_completed', 'architect', 'orchestrator', 'Architect Agent 已完成技术方案与任务清单输出', design_rel)
        self._agent_idle('architect', '技术方案已生成')
        approval_id = self.repo.next_id('approvals', 'approval_id', 'approval_')
        approval = Approval(
            approval_id=approval_id,
            project_id=project_id,
            task_id=task['task_id'],
            approval_type='architecture_review',
            stage='waiting_design_approval',
            target_ref=design_rel,
            artifact_id=design_artifact['artifact_id'],
            status='pending',
            reviewer=DEFAULT_REVIEWER,
            comment='',
            created_at=now_iso(),
            reviewed_at=None,
        )
        self.repo.insert_approval(approval)
        self._event(project_id, task['task_id'], 'approval_created', 'orchestrator', DEFAULT_REVIEWER, '已创建技术方案审批记录', design_rel)
        self._update_project(project_id, status='waiting_design_approval', current_stage='waiting_design_approval')

    def _run_dev_test(self, project_id: str) -> None:
        self._update_project(project_id, status='developing', current_stage='development_testing')
        login_dev = self._create_task(project_id, 'implement_module', '实现登录模块', 'development_testing', 'dev', 'login', 'high', [])
        todo_dev = self._create_task(project_id, 'implement_module', '实现 Todo 模块', 'development_testing', 'dev', 'todo', 'high', [])
        login_test = self._create_task(project_id, 'test_module', '测试登录模块', 'development_testing', 'test', 'login', 'high', [login_dev['task_id']])
        todo_test = self._create_task(project_id, 'test_module', '测试 Todo 模块', 'development_testing', 'test', 'todo', 'high', [todo_dev['task_id']])

        self._run_dev_task(project_id, login_dev, version=1)
        self._run_failed_login_test(project_id, login_test, version=1)
        repair_task = self._create_task(project_id, 'repair_module', '返修登录模块', 'development_testing', 'dev', 'login', 'high', [login_test['task_id']])
        self._run_dev_task(project_id, repair_task, version=2, repaired=True, filename='development/repair_notes/login_repair_v2.md')
        retest_task = self._create_task(project_id, 'retest_module', '重测登录模块', 'development_testing', 'test', 'login', 'high', [repair_task['task_id']])
        self._run_passed_test(project_id, retest_task, version=2, module_name='login', note='返修后登录态校验完整，重测通过。')

        self._run_dev_task(project_id, todo_dev, version=1)
        self._run_passed_test(project_id, todo_test, version=1, module_name='todo', note='待办 CRUD 与状态切换验证通过。')

        self._prepare_final_review(project_id)

    def _run_dev_task(self, project_id: str, task: dict[str, Any], version: int, repaired: bool = False, filename: str | None = None) -> None:
        module_name = task['module_name'] or 'module'
        self._agent_busy('dev', task['task_id'], f'正在实现 {module_name} 模块')
        default_name = f'development/{module_name}_impl_v{version}.md'
        rel_path = filename or default_name
        content = module_impl_markdown(module_name, version, repaired)
        uri = self._write_text(project_id, rel_path, content)
        art_type = 'repair_note' if repaired else 'development_impl'
        self._create_artifact(project_id, task['task_id'], art_type, Path(rel_path).name, uri, version, 'dev')
        summary = '已完成返修说明' if repaired else '已完成模块实现说明'
        self._finish_task(task['task_id'], summary, {'module': module_name, 'version': version})
        self._event(project_id, task['task_id'], 'task_completed', 'dev', 'orchestrator', f'Dev Agent 已完成 {module_name} 模块{ "返修" if repaired else "实现" }', uri)
        self._agent_idle('dev', f'{module_name} 模块任务已完成')

    def _run_failed_login_test(self, project_id: str, task: dict[str, Any], version: int) -> None:
        self._update_project(project_id, status='testing', current_stage='development_testing')
        self._agent_busy('test', task['task_id'], '正在测试 login 模块')
        report_rel = self._write_text(project_id, 'tests/login_test_report_v1.md', test_report_markdown('login', False, version, '首次测试失败，登录态校验不完整。'))
        defect_rel = self._write_text(project_id, 'tests/defect_reports/login_defect_v1.md', defect_markdown('login'))
        self._create_artifact(project_id, task['task_id'], 'test_report', 'login_test_report_v1.md', report_rel, version, 'test')
        self._create_artifact(project_id, task['task_id'], 'defect_report', 'login_defect_v1.md', defect_rel, version, 'test')
        self.repo.update_task(task['task_id'], status='failed', summary='登录模块首次测试失败', result_json={'status': 'need_revision', 'defect_ref': defect_rel}, started_at=task['started_at'] or now_iso(), finished_at=now_iso(), output_ref=report_rel)
        self._event(project_id, task['task_id'], 'test_failed', 'test', 'orchestrator', '登录模块测试失败，已生成缺陷说明', defect_rel)
        self._agent_idle('test', '登录模块首次测试失败，等待返修')
        self._update_project(project_id, status='developing', current_stage='development_testing')

    def _run_passed_test(self, project_id: str, task: dict[str, Any], version: int, module_name: str, note: str) -> None:
        self._update_project(project_id, status='testing', current_stage='development_testing')
        self._agent_busy('test', task['task_id'], f'正在测试 {module_name} 模块')
        suffix = 'retest' if task['task_type'] == 'retest_module' else 'test'
        file_name = f'{module_name}_test_report_v{version}.md'
        rel_path = f'tests/{file_name}'
        report_rel = self._write_text(project_id, rel_path, test_report_markdown(module_name, True, version, note))
        self._create_artifact(project_id, task['task_id'], 'test_report', file_name, report_rel, version, 'test')
        self._finish_task(task['task_id'], f'{module_name} 模块{suffix}通过', {'passed': True, 'module': module_name, 'version': version})
        self._event(project_id, task['task_id'], 'task_completed', 'test', 'orchestrator', f'{module_name} 模块测试通过', report_rel)
        self._agent_idle('test', f'{module_name} 模块测试通过')

    def _prepare_final_review(self, project_id: str) -> None:
        project = self._require_project(project_id)
        self._update_project(project_id, status='reviewing', current_stage='final_review')
        delivery_rel = self._write_text(project_id, 'delivery/delivery_note_v1.md', delivery_note(project['name'], project_id))
        artifact = self._create_artifact(project_id, None, 'delivery_note', 'delivery_note_v1.md', delivery_rel, 1, 'orchestrator')
        approval_id = self.repo.next_id('approvals', 'approval_id', 'approval_')
        approval = Approval(
            approval_id=approval_id,
            project_id=project_id,
            task_id=None,
            approval_type='final_review',
            stage='reviewing',
            target_ref=delivery_rel,
            artifact_id=artifact['artifact_id'],
            status='pending',
            reviewer=DEFAULT_REVIEWER,
            comment='',
            created_at=now_iso(),
            reviewed_at=None,
        )
        self.repo.insert_approval(approval)
        self._event(project_id, None, 'approval_created', 'orchestrator', DEFAULT_REVIEWER, '已创建最终评审记录', delivery_rel)

    def _complete_project(self, project_id: str, reviewer_comment: str) -> None:
        project = self._require_project(project_id)
        summary_rel = self._write_text(project_id, 'delivery/final_summary_v1.md', final_summary(project['name']))
        self._create_artifact(project_id, None, 'final_summary', 'final_summary_v1.md', summary_rel, 1, 'orchestrator')
        self._update_project(project_id, status='done', current_stage='delivery_completed', completed_at=now_iso())
        self._event(project_id, None, 'project_completed', DEFAULT_REVIEWER, 'orchestrator', f'项目已通过最终评审并完成交付。{reviewer_comment}'.strip(), summary_rel)
        self._write_project_meta(project_id)

    def _create_task(self, project_id: str, task_type: str, task_name: str, stage: str, assigned_agent: str, module_name: str | None, priority: str, depends_on: Iterable[str]) -> dict[str, Any]:
        task_id = self.repo.next_id('tasks', 'task_id', 'task_')
        task = Task(
            task_id=task_id,
            project_id=project_id,
            task_type=task_type,
            task_name=task_name,
            stage=stage,
            module_name=module_name,
            assigned_agent=assigned_agent,
            status='processing',
            priority=priority,
            depends_on=list(depends_on),
            input_ref=None,
            output_ref=None,
            retry_count=0,
            max_retry_count=2,
            version=1,
            summary='',
            result_json={},
            created_at=now_iso(),
            started_at=now_iso(),
            finished_at=None,
        )
        self.repo.insert_task(task)
        self._event(project_id, task_id, 'task_created', 'orchestrator', assigned_agent, f'已创建任务：{task_name}', None, {'task_type': task_type, 'module_name': module_name})
        return self.repo.get_task(task_id) or {}

    def _finish_task(self, task_id: str, summary: str, result: dict[str, Any]) -> None:
        self.repo.update_task(task_id, status='done', summary=summary, result_json=result, finished_at=now_iso())

    def _create_artifact(self, project_id: str, task_id: str | None, artifact_type: str, artifact_name: str, uri: str, version: int, generated_by: str, content_type: str = 'markdown') -> dict[str, Any]:
        artifact_id = self.repo.next_id('artifacts', 'artifact_id', 'artifact_')
        artifact = Artifact(
            artifact_id=artifact_id,
            project_id=project_id,
            task_id=task_id,
            artifact_type=artifact_type,
            artifact_name=artifact_name,
            uri=uri,
            version=version,
            generated_by=generated_by,
            status='active',
            content_type=content_type,
            created_at=now_iso(),
        )
        self.repo.insert_artifact(artifact)
        return self.repo.get_artifact(artifact_id) or {}

    def _event(self, project_id: str, task_id: str | None, event_type: str, from_role: str, to_role: str, message: str, related_ref: str | None, metadata: dict[str, Any] | None = None) -> None:
        event_id = self.repo.next_id('events', 'event_id', 'evt_')
        event = Event(
            event_id=event_id,
            project_id=project_id,
            task_id=task_id,
            event_type=event_type,
            from_role=from_role,
            to_role=to_role,
            message=message,
            related_ref=related_ref,
            metadata_json=metadata or {},
            created_at=now_iso(),
        )
        self.repo.insert_event(event)

    def _bootstrap_agent_statuses(self) -> None:
        timestamp = now_iso()
        for agent_id, agent_name in self.AGENTS.items():
            if agent_id == 'orchestrator':
                continue
            self.repo.upsert_agent_status(
                AgentRuntimeStatus(
                    agent_id=agent_id,
                    agent_name=agent_name,
                    status='idle',
                    current_task_id=None,
                    health='healthy',
                    summary='待命中',
                    last_heartbeat_at=timestamp,
                    updated_at=timestamp,
                )
            )

    def _agent_busy(self, agent_id: str, task_id: str, summary: str) -> None:
        timestamp = now_iso()
        self.repo.upsert_agent_status(
            AgentRuntimeStatus(
                agent_id=agent_id,
                agent_name=self.AGENTS[agent_id],
                status='busy',
                current_task_id=task_id,
                health='healthy',
                summary=summary,
                last_heartbeat_at=timestamp,
                updated_at=timestamp,
            )
        )

    def _agent_idle(self, agent_id: str, summary: str) -> None:
        timestamp = now_iso()
        self.repo.upsert_agent_status(
            AgentRuntimeStatus(
                agent_id=agent_id,
                agent_name=self.AGENTS[agent_id],
                status='idle',
                current_task_id=None,
                health='healthy',
                summary=summary,
                last_heartbeat_at=timestamp,
                updated_at=timestamp,
            )
        )

    def _ensure_project_dirs(self, project_id: str) -> None:
        project_root = PROJECTS_DIR / project_id
        paths = [
            project_root / 'metadata',
            project_root / 'requirements',
            project_root / 'prd',
            project_root / 'architecture',
            project_root / 'development',
            project_root / 'development' / 'repair_notes',
            project_root / 'tests',
            project_root / 'tests' / 'defect_reports',
            project_root / 'delivery',
            project_root / 'exports',
        ]
        for path in paths:
            path.mkdir(parents=True, exist_ok=True)

    def _write_text(self, project_id: str, relative_path: str, content: str) -> str:
        target = PROJECTS_DIR / project_id / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')
        return f'projects/{project_id}/{relative_path}'

    def _next_version(self, project_id: str, artifact_type_prefix: str) -> int:
        artifacts = self.repo.list_artifacts(project_id)
        versions = [item['version'] for item in artifacts if item['artifact_type'].startswith(artifact_type_prefix)]
        return max(versions, default=0) + 1

    def _update_project(self, project_id: str, **updates: Any) -> None:
        updates.setdefault('updated_at', now_iso())
        self.repo.update_project(project_id, **updates)
        self._write_project_meta(project_id)

    def _require_project(self, project_id: str) -> dict[str, Any]:
        project = self.repo.get_project(project_id)
        if project is None:
            raise KeyError('PROJECT_NOT_FOUND')
        return project

    def _write_project_meta(self, project_id: str) -> None:
        project = self.repo.get_project(project_id)
        if project is None:
            return
        meta_path = PROJECTS_DIR / project_id / 'metadata' / 'project_meta.json'
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        meta_path.write_text(json.dumps(project, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    def _current_focus(self, project: dict[str, Any], pending_approvals: list[dict[str, Any]], tasks: list[dict[str, Any]]) -> str:
        if project['status'] == 'done':
            return '当前状态：项目已完成，可导出交付包'
        if pending_approvals:
            mapping = {
                'prd_review': '当前等待人工操作：PRD 审批',
                'architecture_review': '当前等待人工操作：技术方案审批',
                'final_review': '当前等待人工操作：最终评审',
            }
            return mapping.get(pending_approvals[0]['approval_type'], '当前等待人工审批')
        active_repair = next((item for item in tasks if item['task_type'] == 'repair_module' and item['status'] in {'processing', 'done'}), None)
        if active_repair:
            return '当前正在执行：登录模块返修'
        return '当前正在执行固定 Pipeline 主链路'

    def _timeline(self, project: dict[str, Any], approvals: list[dict[str, Any]], tasks: list[dict[str, Any]]) -> list[dict[str, str]]:
        approval_map = {item['approval_type']: item for item in approvals}
        def has_task(task_type: str) -> bool:
            return any(item['task_type'] == task_type and item['status'] == 'done' for item in tasks)
        def has_task_prefix(prefix: str) -> bool:
            return any(item['task_type'].startswith(prefix) and item['status'] == 'done' for item in tasks)
        test_failed = any(item['task_type'] == 'test_module' and item['status'] == 'failed' for item in tasks)
        retest_passed = any(item['task_type'] == 'retest_module' and item['status'] == 'done' for item in tasks)
        nodes = [
            ('需求澄清', 'completed' if has_task('clarify_requirement') else 'processing' if project['status'] == 'clarifying' else 'pending'),
            ('PRD 生成', 'completed' if has_task('generate_prd') or has_task('revise_prd') else 'processing' if project['status'] == 'prd_generating' else 'pending'),
            ('PRD 审批', self._approval_node_status(approval_map.get('prd_review'))),
            ('技术方案', 'completed' if has_task('generate_architecture') or has_task('revise_architecture') else 'processing' if project['status'] == 'designing' else 'pending'),
            ('技术方案审批', self._approval_node_status(approval_map.get('architecture_review'))),
            ('开发执行', 'completed' if has_task('implement_module') and any(item['task_type'] == 'repair_module' and item['status'] == 'done' for item in tasks) else 'processing' if project['status'] in {'developing', 'testing'} else 'pending'),
            ('测试验证', 'completed' if retest_passed or project['status'] in {'reviewing', 'delivering', 'done'} else 'failed' if test_failed else 'pending'),
            ('最终评审', self._approval_node_status(approval_map.get('final_review'))),
            ('交付完成', 'completed' if project['status'] == 'done' else 'pending'),
        ]
        return [{'name': name, 'status': status} for name, status in nodes]

    @staticmethod
    def _approval_node_status(approval: dict[str, Any] | None) -> str:
        if approval is None:
            return 'pending'
        status = approval['status']
        if status == 'pending':
            return 'processing'
        if status == 'approved':
            return 'completed'
        if status == 'rejected':
            return 'failed'
        return 'pending'
