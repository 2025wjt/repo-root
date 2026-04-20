# API 设计与前后端交互

## 1. 设计目标

- 简单够用
- 前后端清晰解耦
- 状态查询友好
- 流程控制统一
- 易于联调

## 2. 总体原则

- 前端只通过 API 与系统交互
- 所有关键流程推进都经过 Orchestrator
- 查询接口与操作接口分离
- 返回结构统一
- 错误结构统一

## 3. 统一响应格式

### 成功
```json
{
  "success": true,
  "message": "操作成功",
  "data": {}
}
```

### 失败
```json
{
  "success": false,
  "error_code": "PROJECT_NOT_FOUND",
  "message": "未找到对应项目",
  "details": {
    "project_id": "project_999"
  }
}
```

## 4. MVP 必做接口

### 项目相关
- `POST /api/projects`
- `GET /api/projects/{project_id}`
- `GET /api/projects/{project_id}/overview`

### 任务相关
- `GET /api/projects/{project_id}/tasks`
- `GET /api/tasks/{task_id}`

### 审批相关
- `GET /api/projects/{project_id}/approvals`
- `POST /api/approvals/{approval_id}/submit`

### 产物相关
- `GET /api/projects/{project_id}/artifacts`
- `GET /api/projects/{project_id}/artifacts/{artifact_id}`

### 事件相关
- `GET /api/projects/{project_id}/events`

### 导出相关
- `POST /api/projects/{project_id}/export`

## 5. 核心接口定义

### 5.1 创建项目
`POST /api/projects`

请求体：
```json
{
  "name": "Todo Web App",
  "description": "比赛版演示项目",
  "raw_requirement": "开发一个简单的 Todo Web App，支持登录、待办事项新增删除修改和完成状态切换。"
}
```

返回：
```json
{
  "success": true,
  "message": "项目创建成功",
  "data": {
    "project_id": "project_001",
    "status": "created",
    "current_stage": "project_created"
  }
}
```

### 5.2 项目总览
`GET /api/projects/{project_id}/overview`

返回聚合：
- 项目基础信息
- 当前阶段
- 当前状态
- 任务统计
- 审批统计
- 最近事件
- Agent 状态摘要

### 5.3 任务列表
`GET /api/projects/{project_id}/tasks`

可选参数：
- `stage`
- `status`

### 5.4 审批列表
`GET /api/projects/{project_id}/approvals`

可选参数：
- `status`

### 5.5 提交审批
`POST /api/approvals/{approval_id}/submit`

请求体：
```json
{
  "action": "approved",
  "reviewer": "human_reviewer",
  "comment": "技术方案合理，可以进入开发阶段"
}
```

或：
```json
{
  "action": "rejected",
  "reviewer": "human_reviewer",
  "comment": "模块拆分不清晰，请补充接口说明和任务依赖关系"
}
```

### 5.6 产物列表
`GET /api/projects/{project_id}/artifacts`

可选参数：
- `artifact_type`

### 5.7 单产物内容
`GET /api/projects/{project_id}/artifacts/{artifact_id}`

返回：
- 产物元信息
- 正文内容
- 内容类型（markdown/json）

### 5.8 事件流
`GET /api/projects/{project_id}/events`

可选参数：
- `limit`

### 5.9 导出交付包
`POST /api/projects/{project_id}/export`

请求：
```json
{
  "export_type": "delivery_bundle"
}
```

返回：
```json
{
  "success": true,
  "message": "导出成功",
  "data": {
    "project_id": "project_001",
    "export_file_name": "project_001_delivery_bundle.zip",
    "export_path": "projects/project_001/exports/project_001_delivery_bundle.zip"
  }
}
```

## 6. 页面与接口映射

### 需求输入页
- `POST /api/projects`

### 流程看板页
- `GET /api/projects/{project_id}/overview`
- `GET /api/projects/{project_id}/tasks`
- `GET /api/projects/{project_id}/events`

### 审批页
- `GET /api/projects/{project_id}/approvals`
- `GET /api/projects/{project_id}/artifacts/{artifact_id}`
- `POST /api/approvals/{approval_id}/submit`

### 产物页
- `GET /api/projects/{project_id}/artifacts`
- `GET /api/projects/{project_id}/artifacts/{artifact_id}`

### 导出按钮
- `POST /api/projects/{project_id}/export`

## 7. 刷新策略建议

比赛版建议使用轮询：
- 看板页每 3 到 5 秒轮询一次 `overview`
- 审批提交成功后主动刷新
- 导出成功后刷新产物列表

## 8. 错误码建议

- `PROJECT_NOT_FOUND`
- `TASK_NOT_FOUND`
- `APPROVAL_NOT_FOUND`
- `APPROVAL_ALREADY_PROCESSED`
- `INVALID_APPROVAL_ACTION`
- `ARTIFACT_NOT_FOUND`
- `EXPORT_FAILED`
- `VALIDATION_ERROR`
- `INTERNAL_SERVER_ERROR`
