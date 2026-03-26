"""Orchestrator integration test — requires ANTHROPIC_API_KEY."""

import pytest

from app.schemas.task import StreamEvent, StreamEventType
from app.services.graph import NexusOrchestrator
from tests.conftest import requires_api_key


@requires_api_key
class TestNexusOrchestrator:
    async def test_full_orchestration(self):
        orchestrator = NexusOrchestrator()
        events: list[StreamEvent] = []

        async for event in orchestrator.run(
            "Research what FastAPI is, then write a simple hello world endpoint in Python."
        ):
            events.append(event)

        event_types = {e.event for e in events}
        assert StreamEventType.PLAN in event_types
        assert StreamEventType.DONE in event_types

        done_event = next(e for e in events if e.event == StreamEventType.DONE)
        assert len(done_event.data) > 0

    async def test_plan_creates_subtasks(self):
        orchestrator = NexusOrchestrator()
        plan = await orchestrator._create_plan("Analyze sales data and write a report")
        assert len(plan.subtasks) >= 1
        assert plan.reasoning
