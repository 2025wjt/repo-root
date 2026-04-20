from enum import Enum


class ProjectStatus(str, Enum):
    CREATED = "created"
    CLARIFYING = "clarifying"
    PRD_GENERATING = "prd_generating"
    WAITING_PRD_APPROVAL = "waiting_prd_approval"
    DESIGNING = "designing"
    WAITING_DESIGN_APPROVAL = "waiting_design_approval"
    DEVELOPING = "developing"
    TESTING = "testing"
    REVIEWING = "reviewing"
    DELIVERING = "delivering"
    DONE = "done"
    FAILED = "failed"
    PAUSED = "paused"


class ProjectStage(str, Enum):
    PROJECT_CREATED = "project_created"
    REQUIREMENT_ALIGNMENT = "requirement_alignment"
    PRD_GENERATION = "prd_generation"
    PRD_APPROVAL = "waiting_prd_approval"
    ARCHITECTURE_GENERATION = "architecture_generation"
    ARCHITECTURE_APPROVAL = "waiting_design_approval"
    DEVELOPMENT_TESTING = "development_testing"
    RESULT_REVIEW = "result_review"
    DELIVERY_COMPLETION = "delivery_completion"


class TaskType(str, Enum):
    CLARIFY_REQUIREMENT = "clarify_requirement"
    GENERATE_PRD = "generate_prd"
    REVISE_PRD = "revise_prd"
    GENERATE_ARCHITECTURE = "generate_architecture"
    REVISE_ARCHITECTURE = "revise_architecture"
    SPLIT_TASKS = "split_tasks"
    IMPLEMENT_MODULE = "implement_module"
    REPAIR_MODULE = "repair_module"
    TEST_MODULE = "test_module"
    RETEST_MODULE = "retest_module"


class TaskStatus(str, Enum):
    PENDING = "pending"
    DISPATCHED = "dispatched"
    PROCESSING = "processing"
    WAITING_APPROVAL = "waiting_approval"
    BLOCKED = "blocked"
    WAITING_REPAIR = "waiting_repair"
    RETRYING = "retrying"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ApprovalType(str, Enum):
    PRD_REVIEW = "prd_review"
    DESIGN_REVIEW = "design_review"
    FINAL_REVIEW = "final_review"


class ApprovalAction(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"


class AgentName(str, Enum):
    CLARIFY = "clarify"
    PM = "pm"
    ARCHITECT = "architect"
    DEV = "dev"
    TEST = "test"
    HUMAN_REVIEWER = "human_reviewer"
    ORCHESTRATOR = "orchestrator"


class AgentStatus(str, Enum):
    IDLE = "idle"
    BUSY = "busy"
    WAITING_INPUT = "waiting_input"
    DEGRADED = "degraded"
    OFFLINE = "offline"


class ArtifactType(str, Enum):
    RAW_REQUIREMENT = "raw_requirement"
    STRUCTURED_REQUIREMENT = "structured_requirement"
    PRD = "prd"
    ARCHITECTURE_DESIGN = "architecture_design"
    API_CONTRACT = "api_contract"
    TASK_LIST = "task_list"
    IMPLEMENTATION = "implementation"
    TEST_REPORT = "test_report"
    DEFECT_REPORT = "defect_report"
    DELIVERY_NOTE = "delivery_note"
    FINAL_SUMMARY = "final_summary"


class ArtifactStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
