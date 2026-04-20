# AGENTS.md

## Project mission
Build a competition-grade MVP for an AI-driven requirement delivery workflow engine.

The system must implement this fixed pipeline:

Requirement input
→ structured requirement
→ PRD generation
→ PRD approval
→ architecture generation
→ architecture approval
→ development tasks
→ testing
→ at least one failure-repair-retest loop
→ final review
→ export delivery zip

## Source of truth
Always treat these documents as the source of truth, in priority order:

1. docs/spec/01_比赛版MVP范围冻结.md
2. docs/spec/02_系统总体架构设计.md
3. docs/spec/03_流程与状态机设计.md
4. docs/spec/04_Agent角色与协作协议.md
5. docs/spec/05_数据模型与存储设计.md
6. docs/spec/06_API设计与前后端交互.md
7. docs/spec/07_前端页面与展示设计.md
8. docs/spec/08_开发计划与任务拆分.md

If implementation tradeoffs appear, preserve the MVP scope and the fixed pipeline above.

## Tech stack constraints
- Backend: Python + FastAPI + Pydantic + SQLite
- Frontend: React + Vite
- Artifact format: Markdown + JSON
- Export format: zip
- Prefer minimal dependencies
- Prefer clear folder structure over clever abstractions

## Working rules
- Do not redesign the product scope.
- Do not replace the fixed workflow with free-form agent chat.
- Keep human approval as a real gate.
- Keep the failure → repair → retest loop visible in code and UI.
- Keep all important artifacts persisted to disk.
- Keep all stateful control data in SQLite.
- Before finishing, run the most relevant checks available in the repo.
- When something is ambiguous, choose the simpler MVP implementation and document it.

## Definition of done
The repo is only considered done when:
- a project can be created from the UI
- the pipeline advances through all required stages
- approvals are actionable
- at least one test failure creates a repair task
- artifacts can be viewed
- export generates a delivery zip
