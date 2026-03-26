"""Tests for the in-memory task store — no API key needed."""

import asyncio

import pytest

from app.schemas.task import (
    AgentType,
    StreamEvent,
    StreamEventType,
    SubTask,
    SubTaskResult,
    TaskStatus,
)
from app.services.task_store import task_store


class TestTaskStore:
    async def test_create_task(self):
        task = await task_store.create_task("Test query")
        assert task.status == TaskStatus.PENDING
        assert task.query == "Test query"
        assert task.task_id

    async def test_get_task(self):
        task = await task_store.create_task("Test")
        retrieved = await task_store.get_task(task.task_id)
        assert retrieved is not None
        assert retrieved.task_id == task.task_id

    async def test_get_nonexistent_task(self):
        result = await task_store.get_task("nonexistent")
        assert result is None

    async def test_list_tasks(self):
        await task_store.create_task("First")
        await task_store.create_task("Second")
        tasks = await task_store.list_tasks()
        assert len(tasks) == 2
        # Most recent first
        assert tasks[0].query == "Second"

    async def test_update_status(self):
        task = await task_store.create_task("Test")
        await task_store.update_status(task.task_id, TaskStatus.RUNNING)
        updated = await task_store.get_task(task.task_id)
        assert updated.status == TaskStatus.RUNNING

    async def test_complete_sets_timestamp(self):
        task = await task_store.create_task("Test")
        assert task.completed_at is None
        await task_store.update_status(task.task_id, TaskStatus.COMPLETE)
        updated = await task_store.get_task(task.task_id)
        assert updated.completed_at is not None

    async def test_set_plan(self):
        task = await task_store.create_task("Test")
        plan = [SubTask(id="s1", agent=AgentType.RESEARCH, description="Research")]
        await task_store.set_plan(task.task_id, plan)
        updated = await task_store.get_task(task.task_id)
        assert len(updated.plan) == 1

    async def test_add_result(self):
        task = await task_store.create_task("Test")
        result = SubTaskResult(
            subtask_id="s1",
            agent=AgentType.RESEARCH,
            status=TaskStatus.COMPLETE,
            result="Done",
        )
        await task_store.add_result(task.task_id, result)
        updated = await task_store.get_task(task.task_id)
        assert len(updated.results) == 1

    async def test_set_final_answer(self):
        task = await task_store.create_task("Test")
        await task_store.set_final_answer(task.task_id, "The answer is 42")
        updated = await task_store.get_task(task.task_id)
        assert updated.final_answer == "The answer is 42"

    async def test_subscribe_and_push(self):
        task = await task_store.create_task("Test")
        event = StreamEvent(
            event=StreamEventType.AGENT_START,
            agent=AgentType.RESEARCH,
            data="Starting",
        )
        done_event = StreamEvent(
            event=StreamEventType.DONE,
            agent=AgentType.ORCHESTRATOR,
            data="All done",
        )

        received = []

        async def subscriber():
            async for e in task_store.subscribe(task.task_id):
                received.append(e)

        sub_task = asyncio.create_task(subscriber())
        await asyncio.sleep(0.05)  # Let subscriber start

        await task_store.push_event(task.task_id, event)
        await task_store.push_event(task.task_id, done_event)
        await asyncio.sleep(0.05)

        await sub_task
        assert len(received) == 2
        assert received[0].event == StreamEventType.AGENT_START
        assert received[1].event == StreamEventType.DONE

    async def test_event_replay_on_subscribe(self):
        task = await task_store.create_task("Test")
        event = StreamEvent(
            event=StreamEventType.PLAN,
            agent=AgentType.ORCHESTRATOR,
            data="Plan created",
        )
        done_event = StreamEvent(
            event=StreamEventType.DONE,
            agent=AgentType.ORCHESTRATOR,
            data="Done",
        )
        await task_store.push_event(task.task_id, event)
        await task_store.push_event(task.task_id, done_event)

        received = []
        async for e in task_store.subscribe(task.task_id):
            received.append(e)

        assert len(received) == 2
