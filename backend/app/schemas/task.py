from __future__ import annotations

import enum
from datetime import datetime

from pydantic import BaseModel, Field


class AgentType(str, enum.Enum):
    ORCHESTRATOR = "orchestrator"
    RESEARCH = "research"
    CODE_GEN = "code_gen"
    DATA_ANALYSIS = "data_analysis"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


class StreamEventType(str, enum.Enum):
    PLAN = "plan"
    AGENT_START = "agent_start"
    AGENT_PROGRESS = "agent_progress"
    AGENT_COMPLETE = "agent_complete"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    ERROR = "error"
    DONE = "done"


class TaskRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=10000, description="The complex task to execute")


class SubTask(BaseModel):
    id: str
    agent: AgentType
    description: str
    dependencies: list[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING


class SubTaskResult(BaseModel):
    subtask_id: str
    agent: AgentType
    status: TaskStatus
    result: str = ""
    error: str | None = None
    duration_ms: int = 0


class TaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    query: str
    plan: list[SubTask] = Field(default_factory=list)
    results: list[SubTaskResult] = Field(default_factory=list)
    final_answer: str | None = None
    created_at: datetime
    completed_at: datetime | None = None


class StreamEvent(BaseModel):
    event: StreamEventType
    agent: AgentType | None = None
    data: str
    subtask_id: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
