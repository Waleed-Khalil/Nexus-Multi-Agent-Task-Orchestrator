"""Agent integration tests — require ANTHROPIC_API_KEY."""

import pytest

from app.agents.base import AgentRunner
from app.agents.prompts import RESEARCH_PROMPT, CODEGEN_PROMPT, DATA_ANALYSIS_PROMPT
from app.schemas.agents import ResearchOutput, CodeGenOutput, DataAnalysisOutput
from app.schemas.task import AgentType, StreamEvent, StreamEventType
from app.tools.research import RESEARCH_TOOLS, TOOL_DISPATCH as R_DISPATCH
from app.tools.codegen import CODEGEN_TOOLS, TOOL_DISPATCH as C_DISPATCH
from app.tools.data_analysis import DATA_ANALYSIS_TOOLS, TOOL_DISPATCH as D_DISPATCH
from tests.conftest import requires_api_key


@requires_api_key
class TestResearchAgent:
    async def test_research_agent_returns_valid_output(self):
        runner = AgentRunner(
            agent_type=AgentType.RESEARCH,
            system_prompt=RESEARCH_PROMPT,
            tools=RESEARCH_TOOLS,
            tool_dispatch=R_DISPATCH,
            output_model=ResearchOutput,
        )

        events = []
        output = None
        async for item in runner.run("What is Python? Answer in 1-2 sentences.", "test-1"):
            if isinstance(item, StreamEvent):
                events.append(item)
            elif isinstance(item, ResearchOutput):
                output = item

        assert output is not None
        assert output.summary
        assert 0 <= output.confidence <= 1

        event_types = {e.event for e in events}
        assert StreamEventType.AGENT_START in event_types
        assert StreamEventType.AGENT_COMPLETE in event_types


@requires_api_key
class TestCodeGenAgent:
    async def test_codegen_agent_returns_valid_output(self):
        runner = AgentRunner(
            agent_type=AgentType.CODE_GEN,
            system_prompt=CODEGEN_PROMPT,
            tools=CODEGEN_TOOLS,
            tool_dispatch=C_DISPATCH,
            output_model=CodeGenOutput,
        )

        output = None
        async for item in runner.run(
            "Write a Python function that checks if a number is prime. Keep it simple.",
            "test-2",
        ):
            if isinstance(item, CodeGenOutput):
                output = item

        assert output is not None
        assert "def" in output.code
        assert output.language == "python"


@requires_api_key
class TestDataAnalysisAgent:
    async def test_data_analysis_agent_returns_valid_output(self):
        runner = AgentRunner(
            agent_type=AgentType.DATA_ANALYSIS,
            system_prompt=DATA_ANALYSIS_PROMPT,
            tools=DATA_ANALYSIS_TOOLS,
            tool_dispatch=D_DISPATCH,
            output_model=DataAnalysisOutput,
        )

        output = None
        async for item in runner.run(
            "Analyze the trend: revenue was $100K, $120K, $150K, $130K, $180K over 5 quarters.",
            "test-3",
        ):
            if isinstance(item, DataAnalysisOutput):
                output = item

        assert output is not None
        assert output.analysis
