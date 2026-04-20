PROJECT_STATUSES = [
    'created',
    'clarifying',
    'prd_generating',
    'waiting_prd_approval',
    'designing',
    'waiting_design_approval',
    'developing',
    'testing',
    'reviewing',
    'delivering',
    'done',
    'failed',
    'paused',
]

TASK_STATUSES = [
    'pending',
    'dispatched',
    'processing',
    'waiting_approval',
    'blocked',
    'waiting_repair',
    'retrying',
    'done',
    'failed',
    'cancelled',
]

APPROVAL_STATUSES = ['pending', 'approved', 'rejected', 'expired']
AGENT_STATUSES = ['idle', 'busy', 'waiting_input', 'degraded', 'offline']

TIMELINE_NODES = [
    '需求澄清',
    'PRD 生成',
    'PRD 审批',
    '技术方案',
    '技术方案审批',
    '开发执行',
    '测试验证',
    '最终评审',
    '交付完成',
]
