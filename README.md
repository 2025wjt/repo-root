# AI 驱动的需求交付流程引擎

这是一个围绕固定 Pipeline 的比赛版 MVP：

需求输入 → 结构化需求 → PRD → PRD 审批 → 技术方案 → 技术方案审批 → 开发任务 → 测试任务 → 失败返修 → 最终评审 → 导出 zip

## 当前版本完成内容

- 后端使用 **FastAPI + SQLite + Pydantic**，所有关键控制信息落库
- 前端提供四个固定页面：
  - `/input`
  - `/dashboard`
  - `/approvals`
  - `/artifacts`
- 创建项目后自动执行：
  - 结构化需求生成
  - PRD 生成
  - PRD 审批记录创建
- PRD 审批通过后自动执行：
  - 技术方案生成
  - API 说明生成
  - 任务清单生成
  - 技术方案审批记录创建
- 技术方案审批通过后自动执行：
  - login / todo 开发任务
  - login / todo 测试任务
  - login 首轮测试失败
  - defect 生成
  - repair 任务创建
  - retest 通过
  - 最终评审记录创建
- 产物页可查看 Markdown / JSON 文档
- 可导出交付 zip 包

## 目录结构

```text
repo-root/
├── AGENTS.md
├── backend/
│   ├── requirements.txt
│   └── app/
├── frontend/
├── data/
├── docs/spec/
├── projects/
├── scripts/
└── .env.example
```

## 后端启动

### 手动启动

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python scripts/init_db.py
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

### 脚本启动

```bash
bash scripts/run_backend.sh
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_backend.ps1
```

## 前端启动

> 为了保证离线环境也能稳定运行，当前前端使用本地静态 React 运行方式，不依赖在线安装额外 npm 包。

### 启动命令

```bash
cd frontend
npm run dev
```

或：

```bash
python scripts/serve_frontend.py
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_frontend.ps1
```

前端地址：

- http://127.0.0.1:5173/input
- http://127.0.0.1:5173/dashboard
- http://127.0.0.1:5173/approvals
- http://127.0.0.1:5173/artifacts

## 最小演示流程

1. 打开 `/input` 创建项目
2. 系统自动推进到 PRD 审批
3. 在 `/approvals` 通过 PRD 审批
4. 系统自动推进到技术方案审批
5. 在 `/approvals` 通过技术方案审批
6. 系统自动跑完开发/测试任务，并展示 login 模块失败 → 返修 → 重测通过
7. 在 `/approvals` 通过最终评审
8. 在 `/artifacts` 查看关键文档并导出 zip

## 演示验证脚本

```bash
python scripts/demo_flow.py
```

该脚本会自动：
- 创建项目
- 通过 PRD 审批
- 通过技术方案审批
- 通过最终评审
- 导出交付 zip

## 说明

- 所有关键状态推进仅由 Orchestrator 控制
- 数据库存事实，文件系统存正文与导出包
- 失败回流为固定案例：login 首轮测试失败、生成缺陷、返修后重测通过
