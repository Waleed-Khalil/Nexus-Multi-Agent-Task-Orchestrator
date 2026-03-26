"""Tests for Pydantic schemas — these run without an API key."""

import pytest
from pydantic import ValidationError

from app.schemas.task import (
    AgentType,
    StreamEvent,
    StreamEventType,
    SubTask,
    SubTaskResult,
    TaskRequest,
    TaskResponse,
    TaskStatus,
)
from app.schemas.agents import (
    CodeGenInput,
    CodeGenOutput,
    DataAnalysisInput,
    DataAnalysisOutput,
    OrchestratorPlan,
    ResearchInput,
    ResearchOutput,
)


class TestTaskRequest:
    def test_valid_request(self):
        req = TaskRequest(query="Analyze sales data")
        assert req.query == "Analyze sales data"

    def test_empty_query_rejected(self):
        with pytest.raises(ValidationError):
            TaskRequest(query="")

    def test_max_length_enforced(self):
        with pytest.raises(ValidationError):
            TaskRequest(query="x" * 10001)


class TestSubTask:
    def test_defaults(self):
        st = SubTask(id="st-1", agent=AgentType.RESEARCH, description="Look something up")
        assert st.status == TaskStatus.PENDING
        assert st.dependencies == []

    def test_with_dependencies(self):
        st = SubTask(
            id="st-2",
            agent=AgentType.CODE_GEN,
            description="Write code",
            dependencies=["st-1"],
        )
        assert st.dependencies == ["st-1"]


class TestSubTaskResult:
    def test_complete_result(self):
        r = SubTaskResult(
            subtask_id="st-1",
            agent=AgentType.RESEARCH,
            status=TaskStatus.COMPLETE,
            result="Found the answer",
            duration_ms=1234,
        )
        assert r.error is None
        assert r.duration_ms == 1234

    def test_failed_result(self):
        r = SubTaskResult(
            subtask_id="st-1",
            agent=AgentType.CODE_GEN,
            status=TaskStatus.FAILED,
            error="Timeout",
        )
        assert r.result == ""


class TestTaskResponse:
    def test_minimal(self):
        from datetime import datetime

        t = TaskResponse(
            task_id="abc",
            status=TaskStatus.PENDING,
            query="test",
            created_at=datetime.utcnow(),
        )
        assert t.final_answer is None
        assert t.plan == []
        assert t.results == []


class TestStreamEvent:
    def test_with_agent(self):
        e = StreamEvent(
            event=StreamEventType.AGENT_START,
            agent=AgentType.RESEARCH,
            data="Starting",
        )
        assert e.subtask_id is None

    def test_with_subtask(self):
        e = StreamEvent(
            event=StreamEventType.TOOL_CALL,
            agent=AgentType.CODE_GEN,
            data="Calling validate_python",
            subtask_id="st-1",
        )
        assert e.subtask_id == "st-1"


class TestResearchSchemas:
    def test_input_defaults(self):
        inp = ResearchInput(query="What is LangGraph?")
        assert inp.depth == "standard"
        assert inp.context == ""

    def test_output_confidence_bounds(self):
        out = ResearchOutput(summary="test", confidence=0.9)
        assert out.confidence == 0.9

        with pytest.raises(ValidationError):
            ResearchOutput(summary="test", confidence=1.5)

        with pytest.raises(ValidationError):
            ResearchOutput(summary="test", confidence=-0.1)


class TestCodeGenSchemas:
    def test_input_defaults(self):
        inp = CodeGenInput(specification="Write a hello world")
        assert inp.language == "python"

    def test_output(self):
        out = CodeGenOutput(code="print('hi')", language="python")
        assert out.explanation == ""
        assert out.dependencies == []


class TestDataAnalysisSchemas:
    def test_input(self):
        inp = DataAnalysisInput(question="What's the trend?")
        assert inp.data_description == ""

    def test_output(self):
        out = DataAnalysisOutput(analysis="Upward trend detected")
        assert out.methodology == ""
        assert out.conclusions == []
        assert out.visualizations == []


class TestOrchestratorPlan:
    def test_plan(self):
        plan = OrchestratorPlan(
            reasoning="Split into research then code",
            subtasks=[
                SubTask(id="s1", agent=AgentType.RESEARCH, description="Research"),
                SubTask(
                    id="s2",
                    agent=AgentType.CODE_GEN,
                    description="Code",
                    dependencies=["s1"],
                ),
            ],
        )
        assert len(plan.subtasks) == 2
        assert plan.subtasks[1].dependencies == ["s1"]
