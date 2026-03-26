"""LangGraph-based orchestration engine that manages the agent state machine."""

from __future__ import annotations

import json
import logging
import uuid
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Annotated, Any, TypedDict

import anthropic
from langgraph.graph import END, StateGraph
from pydantic import BaseModel

from app.agents.base import AgentRunner
from app.agents.prompts import (
    CODEGEN_PROMPT,
    DATA_ANALYSIS_PROMPT,
    ORCHESTRATOR_PROMPT,
    RESEARCH_PROMPT,
)
from app.config import get_settings
from app.schemas.agents import (
    CodeGenOutput,
    DataAnalysisOutput,
    OrchestratorPlan,
    ResearchOutput,
)
from app.schemas.task import (
    AgentType,
    StreamEvent,
    StreamEventType,
    SubTask,
    SubTaskResult,
    TaskStatus,
)
from app.tools.codegen import CODEGEN_TOOLS
from app.tools.codegen import TOOL_DISPATCH as CODEGEN_DISPATCH
from app.tools.data_analysis import DATA_ANALYSIS_TOOLS
from app.tools.data_analysis import TOOL_DISPATCH as DATA_DISPATCH
from app.tools.research import RESEARCH_TOOLS
from app.tools.research import TOOL_DISPATCH as RESEARCH_DISPATCH

logger = logging.getLogger(__name__)


def _merge_results(
    existing: list[SubTaskResult], new: list[SubTaskResult]
) -> list[SubTaskResult]:
    """Merge subtask results, keeping the latest for each subtask_id."""
    by_id = {r.subtask_id: r for r in existing}
    for r in new:
        by_id[r.subtask_id] = r
    return list(by_id.values())


class GraphState(TypedDict):
    query: str
    plan: list[SubTask]
    results: Annotated[list[SubTaskResult], _merge_results]
    current_subtask_idx: int
    final_answer: str
    events: list[StreamEvent]


def build_agent_runner(agent_type: AgentType, client: anthropic.AsyncAnthropic) -> AgentRunner:
    """Factory to build the right AgentRunner for a given agent type."""
    config = {
        AgentType.RESEARCH: (RESEARCH_PROMPT, RESEARCH_TOOLS, RESEARCH_DISPATCH, ResearchOutput),
        AgentType.CODE_GEN: (CODEGEN_PROMPT, CODEGEN_TOOLS, CODEGEN_DISPATCH, CodeGenOutput),
        AgentType.DATA_ANALYSIS: (
            DATA_ANALYSIS_PROMPT,
            DATA_ANALYSIS_TOOLS,
            DATA_DISPATCH,
            DataAnalysisOutput,
        ),
    }
    prompt, tools, dispatch, model = config[agent_type]
    return AgentRunner(
        agent_type=agent_type,
        system_prompt=prompt,
        tools=tools,
        tool_dispatch=dispatch,
        output_model=model,
        client=client,
    )


class NexusOrchestrator:
    """Main orchestration engine that decomposes tasks and routes to agents via LangGraph."""

    def __init__(self, client: anthropic.AsyncAnthropic | None = None):
        settings = get_settings()
        self.client = client or anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.model_name

    async def run(self, query: str) -> AsyncIterator[StreamEvent]:
        """Execute the full orchestration pipeline, yielding stream events."""

        # Step 1: Plan
        yield StreamEvent(
            event=StreamEventType.AGENT_START,
            agent=AgentType.ORCHESTRATOR,
            data="Analyzing request and creating execution plan",
        )

        plan = await self._create_plan(query)

        yield StreamEvent(
            event=StreamEventType.PLAN,
            agent=AgentType.ORCHESTRATOR,
            data=json.dumps(
                {"reasoning": plan.reasoning, "subtasks": [st.model_dump() for st in plan.subtasks]},
                default=str,
            ),
        )

        # Step 2: Execute subtasks in dependency order
        completed: dict[str, SubTaskResult] = {}
        for subtask in plan.subtasks:
            # Build context from dependencies
            dep_context = ""
            for dep_id in subtask.dependencies:
                if dep_id in completed:
                    dep_context += f"\n--- Result from {dep_id} ---\n{completed[dep_id].result}\n"

            agent_input = self._build_agent_input(subtask, dep_context)

            runner = build_agent_runner(subtask.agent, self.client)
            start_time = datetime.utcnow()
            result_text = ""

            try:
                async for event in runner.run(agent_input, subtask.id):
                    if isinstance(event, StreamEvent):
                        yield event
                    elif isinstance(event, BaseModel):
                        result_text = event.model_dump_json(indent=2)

                duration = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                completed[subtask.id] = SubTaskResult(
                    subtask_id=subtask.id,
                    agent=subtask.agent,
                    status=TaskStatus.COMPLETE,
                    result=result_text,
                    duration_ms=duration,
                )
            except Exception as e:
                logger.exception("Subtask %s failed", subtask.id)
                duration = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                completed[subtask.id] = SubTaskResult(
                    subtask_id=subtask.id,
                    agent=subtask.agent,
                    status=TaskStatus.FAILED,
                    error=str(e),
                    duration_ms=duration,
                )
                yield StreamEvent(
                    event=StreamEventType.ERROR,
                    agent=subtask.agent,
                    data=f"Subtask {subtask.id} failed: {e}",
                    subtask_id=subtask.id,
                )

        # Step 3: Synthesize final answer
        final = await self._synthesize(query, list(completed.values()))
        yield StreamEvent(
            event=StreamEventType.DONE,
            agent=AgentType.ORCHESTRATOR,
            data=final,
        )

    async def _create_plan(self, query: str) -> OrchestratorPlan:
        """Use Claude to decompose the query into subtasks."""
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=ORCHESTRATOR_PROMPT,
            messages=[{"role": "user", "content": query}],
        )

        text = response.content[0].text
        # Extract JSON
        json_str = text
        if "```json" in text:
            json_str = text.split("```json")[1].split("```")[0].strip()
        elif "{" in text:
            start = text.index("{")
            end = text.rindex("}") + 1
            json_str = text[start:end]

        data = json.loads(json_str)

        # Ensure IDs and fix agent enum values
        subtasks = []
        for i, st in enumerate(data.get("subtasks", [])):
            st.setdefault("id", f"subtask-{i + 1}")
            st.setdefault("dependencies", [])
            st["status"] = TaskStatus.PENDING
            subtasks.append(SubTask.model_validate(st))

        return OrchestratorPlan(
            reasoning=data.get("reasoning", ""),
            subtasks=subtasks,
        )

    def _build_agent_input(self, subtask: SubTask, dep_context: str) -> str:
        """Build the user message for a sub-agent."""
        msg = f"Task: {subtask.description}"
        if dep_context:
            msg += f"\n\nContext from previous steps:\n{dep_context}"
        return msg

    async def _synthesize(self, query: str, results: list[SubTaskResult]) -> str:
        """Synthesize all subtask results into a final cohesive answer."""
        results_text = ""
        for r in results:
            status = "completed" if r.status == TaskStatus.COMPLETE else "failed"
            results_text += f"\n### Subtask {r.subtask_id} ({r.agent.value}) — {status}\n"
            if r.result:
                results_text += r.result + "\n"
            if r.error:
                results_text += f"Error: {r.error}\n"

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=(
                "You are the Nexus Orchestrator synthesizer. Combine the results from all "
                "sub-agents into a clear, cohesive final answer for the user. Be comprehensive "
                "but concise. Format with markdown."
            ),
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Original request: {query}\n\n"
                        f"Sub-agent results:\n{results_text}\n\n"
                        "Please synthesize these into a final comprehensive answer."
                    ),
                }
            ],
        )
        return response.content[0].text
