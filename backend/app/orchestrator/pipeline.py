from dataclasses import dataclass


@dataclass(frozen=True)
class PipelineNode:
    key: str
    label: str
    requires_approval: bool = False


FIXED_PIPELINE = [
    PipelineNode(key="requirement_input", label="需求提交"),
    PipelineNode(key="structured_requirement", label="需求澄清"),
    PipelineNode(key="prd_generation", label="PRD 生成"),
    PipelineNode(key="prd_approval", label="PRD 审批", requires_approval=True),
    PipelineNode(key="architecture_generation", label="技术方案生成"),
    PipelineNode(key="architecture_approval", label="技术方案审批", requires_approval=True),
    PipelineNode(key="development_tasks", label="开发任务执行"),
    PipelineNode(key="testing", label="测试验证"),
    PipelineNode(key="repair_loop", label="失败返修重测"),
    PipelineNode(key="final_review", label="最终评审", requires_approval=True),
    PipelineNode(key="delivery_export", label="交付导出"),
]
