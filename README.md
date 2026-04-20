# AI 驱动的需求交付流程引擎

比赛版 MVP 的当前仓库状态是“可继续开发的初始框架”，严格按 `AGENTS.md` 和 `docs/spec/01` 到 `08` 约束搭建。

## 当前目标

这一步只完成基础工程底座，不追求完整业务闭环：

- 固定 Pipeline 的目录和模块边界先冻结
- 后端提供 FastAPI + SQLite 的可运行骨架
- 前端提供 React + Vite 的四页面入口骨架
- 根目录补齐数据目录、启动脚本和环境示例

## 目录结构

```text
repo-root/
├── AGENTS.md
├── backend/
├── data/
├── docs/
├── frontend/
├── projects/
├── scripts/
└── .env.example
```

## 已具备的基础能力

- 后端应用可启动，并在启动时初始化 SQLite 表结构和运行目录
- 后端已提供 `GET /health` 和一组与 spec 对齐的基础 API 路由骨架
- `POST /api/projects` 已可创建项目记录，并把原始需求落到 `projects/<project_id>/requirements/raw_requirement_v1.md`
- 前端应用可启动，并提供四个固定页面入口：
  - `/input`
  - `/dashboard`
  - `/approvals`
  - `/artifacts`
- 需求输入页已预留并接入创建项目请求

## 快速启动

### 后端

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_backend.ps1
```

手动方式：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir .\backend --reload
```

### 前端

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_frontend.ps1
```

手动方式：

```powershell
cd .\frontend
npm install
npm run dev
```

## 初始化数据库

```powershell
python .\scripts\init_db.py
```

## 当前刻意未完成的部分

以下内容仍然只是骨架或占位，留待下一阶段真正功能开发：

- 完整 Orchestrator 主链路推进
- PRD / 技术方案审批记录自动生成
- 开发任务、测试任务与失败返修重测闭环
- 真实产物读取与前端联动
- 最终评审逻辑
- 交付 zip 的完整目录装配

## 设计取舍

- 优先固定目录、枚举、协议和 API 外形，避免后续大改结构
- 控制信息继续放 SQLite，业务产物继续放文件系统
- 前端先用轻量自定义路由和组件，不引入大型 UI 框架
- 先保证“能跑起来”，再进入真正功能开发阶段

