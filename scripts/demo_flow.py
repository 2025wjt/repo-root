from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))

from app.db import Database
from app.orchestrator import Orchestrator
from app.repository import Repository


def main() -> None:
    db = Database()
    db.init()
    repo = Repository(db)
    orchestrator = Orchestrator(repo)

    project = orchestrator.create_project(
        'Todo Web App',
        '比赛版演示项目',
        '开发一个简单的 Todo Web App，支持用户登录、待办事项新增删除修改和完成状态切换。',
    )
    project_id = project['project_id']
    approvals = repo.list_approvals(project_id)
    prd_approval = next(item for item in approvals if item['approval_type'] == 'prd_review' and item['status'] == 'pending')
    orchestrator.submit_approval(prd_approval['approval_id'], 'approved', 'human_reviewer', 'PRD 内容完整，可以继续')
    approvals = repo.list_approvals(project_id)
    design_approval = next(item for item in approvals if item['approval_type'] == 'architecture_review' and item['status'] == 'pending')
    orchestrator.submit_approval(design_approval['approval_id'], 'approved', 'human_reviewer', '技术方案合理，进入开发测试')
    approvals = repo.list_approvals(project_id)
    final_approval = next(item for item in approvals if item['approval_type'] == 'final_review' and item['status'] == 'pending')
    orchestrator.submit_approval(final_approval['approval_id'], 'approved', 'human_reviewer', '结果满足比赛版 MVP 要求')
    export_result = orchestrator.export_project(project_id)
    overview = orchestrator.overview(project_id)
    print(json.dumps({'project_id': project_id, 'overview': overview, 'export': export_result}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
