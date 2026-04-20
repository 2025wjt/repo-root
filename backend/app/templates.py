from __future__ import annotations

import json
from textwrap import dedent
from typing import Any


def structured_requirement_markdown(project_name: str, raw_requirement: str) -> str:
    return dedent(
        f'''
        # 结构化需求单

        ## 项目名称
        {project_name}

        ## 原始需求摘要
        {raw_requirement.strip()}

        ## 用户角色
        - 普通用户：登录后管理个人待办事项

        ## 核心功能点
        1. 用户登录
        2. 待办事项新增
        3. 待办事项删除
        4. 待办事项修改
        5. 待办事项完成/未完成状态切换

        ## 约束条件
        - 比赛版 MVP
        - 演示优先，流程稳定优先
        - 保留人工审批节点
        - 至少演示一次失败返修回流

        ## 验收边界
        - 重点演示固定 Pipeline 能跑通
        - 不追求真实生产级鉴权与持久化
        '''
    ).strip() + '\n'


def structured_requirement_json(project_name: str, raw_requirement: str) -> str:
    payload: dict[str, Any] = {
        'project_name': project_name,
        'summary': raw_requirement.strip(),
        'roles': ['end_user'],
        'features': [
            'user_login',
            'todo_create',
            'todo_delete',
            'todo_update',
            'todo_toggle_status',
        ],
        'constraints': [
            'competition_mvp',
            'fixed_pipeline',
            'human_approval_required',
            'visible_repair_loop',
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + '\n'


def prd_markdown(project_name: str, raw_requirement: str, revision_note: str = '') -> str:
    revision_block = f'\n## 修订说明\n- {revision_note}\n' if revision_note else ''
    return dedent(
        f'''
        # PRD

        ## 目标
        基于原始需求实现一个可用于比赛演示的 Todo Web App 交付流程案例，验证 AI 驱动的需求交付流程引擎能够完成从需求到交付的闭环。

        ## 项目
        {project_name}

        ## 原始需求摘要
        {raw_requirement.strip()}

        ## 功能范围
        - 登录
        - 待办新增
        - 待办删除
        - 待办修改
        - 待办完成/未完成切换

        ## 用户故事
        1. 作为用户，我希望可以登录系统。
        2. 作为用户，我希望创建、修改、删除待办事项。
        3. 作为用户，我希望切换待办完成状态。

        ## 验收标准
        - 系统可完成两次文档审批。
        - 系统会生成开发任务与测试任务。
        - 登录模块第一次测试失败并触发返修。
        - 最终可导出交付 zip 包。

        ## 优先级
        - P0：登录、待办 CRUD、状态切换
        - P1：演示可视化、导出交付包
        {revision_block}
        '''
    ).strip() + '\n'


def architecture_markdown(project_name: str, revision_note: str = '') -> str:
    revision_block = f'\n## 修订说明\n- {revision_note}\n' if revision_note else ''
    return dedent(
        f'''
        # 技术方案

        ## 项目
        {project_name}

        ## 技术栈
        - Backend: FastAPI + SQLite + Pydantic
        - Frontend: React 前端展示层
        - Artifact: Markdown / JSON
        - Export: zip

        ## 模块划分
        - login 模块：登录表单、登录态校验说明
        - todo 模块：待办列表、CRUD、状态切换
        - workflow 模块：项目看板、审批页、产物页

        ## 关键流程
        1. 需求进入 Orchestrator
        2. 生成结构化需求、PRD、技术方案
        3. 审批通过后创建开发和测试任务
        4. login 模块第一次测试失败并触发 repair
        5. 全部通过后进入最终评审与导出

        ## 风险控制
        - 失败回流逻辑固定，不随机化
        - 所有关键状态由 Orchestrator 推进
        - 所有产物同时落库索引并落盘
        {revision_block}
        '''
    ).strip() + '\n'


def api_contract_markdown() -> str:
    return dedent(
        '''
        # API 说明

        ## Backend API
        - POST /api/projects
        - GET /api/projects/{project_id}
        - GET /api/projects/{project_id}/overview
        - GET /api/projects/{project_id}/tasks
        - GET /api/tasks/{task_id}
        - GET /api/projects/{project_id}/approvals
        - POST /api/approvals/{approval_id}/submit
        - GET /api/projects/{project_id}/artifacts
        - GET /api/projects/{project_id}/artifacts/{artifact_id}
        - GET /api/projects/{project_id}/events
        - POST /api/projects/{project_id}/export

        ## 关键前端交互
        - 输入页创建项目
        - 审批页提交通过/驳回
        - 产物页读取文档与导出 zip
        '''
    ).strip() + '\n'


def task_list_json(project_id: str) -> str:
    payload = {
        'project_id': project_id,
        'development_tasks': [
            {'module': 'login', 'task_type': 'implement_module', 'goal': '实现登录模块'},
            {'module': 'todo', 'task_type': 'implement_module', 'goal': '实现待办 CRUD 与状态切换'},
        ],
        'testing_tasks': [
            {'module': 'login', 'task_type': 'test_module', 'goal': '验证登录模块'},
            {'module': 'todo', 'task_type': 'test_module', 'goal': '验证待办模块'},
        ],
        'repair_rule': 'login 模块第一次测试失败后创建 repair_module 与 retest_module',
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + '\n'


def module_impl_markdown(module_name: str, version: int, repaired: bool = False) -> str:
    fix = '已补充登录态校验、错误分支与状态说明。' if repaired else '已完成比赛版 MVP 所需的模块实现说明。'
    return dedent(
        f'''
        # {module_name} 模块实现说明

        - 模块：{module_name}
        - 版本：v{version}
        - 类型：{'返修实现' if repaired else '首次实现'}

        ## 实现摘要
        {fix}

        ## 关键点
        - 使用模板化实现确保演示稳定
        - 为测试报告提供可校验的交付说明
        '''
    ).strip() + '\n'


def test_report_markdown(module_name: str, passed: bool, version: int, note: str) -> str:
    result = 'PASS' if passed else 'FAIL'
    return dedent(
        f'''
        # {module_name} 模块测试报告

        - 版本：v{version}
        - 结论：{result}

        ## 检查项
        - 功能覆盖
        - 交互流程
        - 状态回写

        ## 结果说明
        {note}
        '''
    ).strip() + '\n'


def defect_markdown(module_name: str) -> str:
    return dedent(
        f'''
        # {module_name} 模块缺陷说明

        ## 结论
        首轮测试未通过。

        ## 缺陷原因
        登录态校验不完整，异常场景说明缺失，导致测试报告判定为失败。

        ## 返修建议
        - 补充登录态校验逻辑说明
        - 明确失败场景处理
        - 返修后重新测试
        '''
    ).strip() + '\n'


def delivery_note(project_name: str, project_id: str) -> str:
    return dedent(
        f'''
        # 交付说明

        - 项目：{project_name}
        - 项目编号：{project_id}

        ## 交付内容
        - 结构化需求单
        - PRD
        - 技术方案与 API 说明
        - 任务清单
        - 开发实现说明
        - 测试报告与缺陷说明
        - 最终总结

        ## 评审建议
        当前版本满足比赛版 MVP 演示要求，可进入最终人工评审。
        '''
    ).strip() + '\n'


def final_summary(project_name: str) -> str:
    return dedent(
        f'''
        # 最终交付总结

        {project_name} 已完成固定 Pipeline：需求输入 → 结构化需求 → PRD → PRD 审批 → 技术方案 → 技术方案审批 → 开发测试 → 失败返修 → 最终评审 → 交付导出。

        ## 演示亮点
        - 两次人工审批门禁
        - login 模块失败返修回流
        - 关键产物全量落盘
        - 导出交付 zip 可直接展示
        '''
    ).strip() + '\n'
