# Agent 角色与协作协议

## 1. 设计目标

- 职责清晰
- 协议统一
- 结果可控
- 可替换
- 可展示

## 2. Agent 总览

比赛版保留：
- Clarify Agent
- PM Agent
- Architect Agent
- Dev Agent
- Test Agent
- Human Reviewer（人工角色）
- Orchestrator（系统编排角色）

## 3. 各 Agent 职责

### 3.1 Clarify Agent
负责：
- 识别项目目标
- 提取功能点
- 识别用户角色
- 识别约束条件
- 输出结构化需求单

不负责：
- 不生成 PRD
- 不做技术方案
- 不做审批决策

### 3.2 PM Agent
负责：
- 生成 PRD
- 定义验收标准
- 给出优先级建议

不负责：
- 不做技术架构决策
- 不做开发实现
- 不做人工审批

### 3.3 Architect Agent
负责：
- 输出技术栈建议
- 设计模块划分
- 输出接口说明
- 拆分开发任务与测试任务

不负责：
- 不直接编码
- 不直接审批
- 不直接修改项目状态

### 3.4 Dev Agent
负责：
- 根据任务说明完成模块实现
- 输出开发摘要
- 接收返修任务并修复缺陷

不负责：
- 不决定流程走向
- 不决定是否进入测试
- 不绕过审批

### 3.5 Test Agent
负责：
- 执行测试验证
- 输出测试结果
- 标记是否通过
- 失败时给出缺陷说明

不负责：
- 不修复缺陷
- 不决定最终交付通过

### 3.6 Human Reviewer
负责：
- PRD 审批
- 技术方案审批
- 最终交付评审

## 4. Orchestrator 与 Agent 的关系

- Orchestrator 是调度者
- Agent 是执行者

### Orchestrator 负责
- 创建任务
- 派发任务
- 构造输入
- 接收输出
- 校验输出
- 更新状态
- 决定下一步流转

### Agent 负责
- 读取任务输入
- 生成任务结果
- 输出结构化内容
- 上报执行摘要

## 5. Agent 协作主链路

```text
Clarify Agent
  ↓
PM Agent
  ↓
Human Reviewer（PRD 审批）
  ↓
Architect Agent
  ↓
Human Reviewer（技术方案审批）
  ↓
Dev Agent
  ↓
Test Agent
  ├─ 若失败 → Dev Agent 返修 → Test Agent 重测
  └─ 若通过 → Human Reviewer（最终评审）
```

## 6. 统一输入协议

每个 Agent 接收统一 Task Envelope：

```json
{
  "task_id": "task_prd_001",
  "project_id": "project_001",
  "task_type": "generate_prd",
  "assigned_agent": "pm",
  "stage": "prd_generation",
  "version": 1,
  "input_data": {
    "requirement_summary": "开发一个 Todo Web App",
    "structured_requirement_ref": "projects/project_001/requirements/structured_requirement.md"
  },
  "context": {
    "upstream_artifacts": [
      "projects/project_001/requirements/structured_requirement.md"
    ],
    "constraints": [
      "比赛版 MVP",
      "优先演示完整流程"
    ]
  },
  "expected_output": {
    "artifact_type": "prd",
    "format": "markdown"
  }
}
```

## 7. 统一输出协议

每个 Agent 输出统一 Agent Result：

```json
{
  "task_id": "task_prd_001",
  "project_id": "project_001",
  "agent": "pm",
  "status": "done",
  "summary": "已完成 PRD 生成，包含功能列表、验收标准和优先级说明。",
  "artifacts": [
    {
      "artifact_type": "prd",
      "artifact_name": "prd.md",
      "artifact_uri": "projects/project_001/prd/prd.md"
    }
  ],
  "result_data": {
    "next_hint": "等待 PRD 审批",
    "quality_note": "内容完整，可进入人工审核"
  },
  "errors": []
}
```

## 8. 输出状态规范

Agent 只允许返回：
- `done`
- `failed`
- `need_revision`
- `blocked`

## 9. 任务类型映射

```text
clarify_requirement   → Clarify Agent
generate_prd          → PM Agent
revise_prd            → PM Agent
generate_architecture → Architect Agent
revise_architecture   → Architect Agent
split_tasks           → Architect Agent
implement_module      → Dev Agent
repair_module         → Dev Agent
test_module           → Test Agent
retest_module         → Test Agent
```

## 10. 返修场景协议

### 测试失败时
Test Agent 输出：
- `status = need_revision`
- 缺陷说明
- 关联开发产物
- 返修建议

### Orchestrator 处理
- 保留测试报告
- 创建 `repair_module`
- 将返修意见写入上下文
- 派发给 Dev Agent

### Dev Agent 修复后
- 输出修复摘要
- 输出新版本模块结果

### Test Agent 重测
- Orchestrator 创建 `retest_module`

## 11. 双模式执行建议

### Mock 模式
- 输出稳定
- 便于演示
- 便于测试流程闭环

### LLM 模式
- 更像真实 AI 协作
- 更适合 Clarify / PM / Architect

### 比赛版建议
- Clarify / PM / Architect：优先接 LLM
- Dev / Test：可先用模板化或半模拟
- 必须保留 Mock 开关兜底
