"""In-memory task store with async event streaming."""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import AsyncIterator
from datetime import datetime

from app.schemas.task import (
    StreamEvent,
    StreamEventType,
    SubTask,
    SubTaskResult,
    TaskResponse,
    TaskStatus,
)


class TaskStore:
    """Thread-safe in-memory store for task state and SSE event queues."""

    def __init__(self):
        self._tasks: dict[str, TaskResponse] = {}
        self._events: dict[str, list[StreamEvent]] = {}
        self._queues: dict[str, list[asyncio.Queue[StreamEvent | None]]] = {}
        self._lock = asyncio.Lock()

    async def create_task(self, query: str) -> TaskResponse:
        task_id = str(uuid.uuid4())
        task = TaskResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            query=query,
            created_at=datetime.utcnow(),
        )
        async with self._lock:
            self._tasks[task_id] = task
            self._events[task_id] = []
            self._queues[task_id] = []
        return task

    async def get_task(self, task_id: str) -> TaskResponse | None:
        return self._tasks.get(task_id)

    async def list_tasks(self) -> list[TaskResponse]:
        return list(reversed(self._tasks.values()))

    async def update_status(self, task_id: str, status: TaskStatus):
        if task_id in self._tasks:
            self._tasks[task_id].status = status
            if status == TaskStatus.COMPLETE:
                self._tasks[task_id].completed_at = datetime.utcnow()

    async def set_plan(self, task_id: str, plan: list[SubTask]):
        if task_id in self._tasks:
            self._tasks[task_id].plan = plan

    async def add_result(self, task_id: str, result: SubTaskResult):
        if task_id in self._tasks:
            self._tasks[task_id].results.append(result)

    async def set_final_answer(self, task_id: str, answer: str):
        if task_id in self._tasks:
            self._tasks[task_id].final_answer = answer

    async def push_event(self, task_id: str, event: StreamEvent):
        """Push an event to all active subscribers and the event log."""
        async with self._lock:
            if task_id in self._events:
                self._events[task_id].append(event)
            for queue in self._queues.get(task_id, []):
                await queue.put(event)

    async def subscribe(self, task_id: str) -> AsyncIterator[StreamEvent]:
        """Subscribe to live events for a task. Yields events as they arrive."""
        queue: asyncio.Queue[StreamEvent | None] = asyncio.Queue()
        async with self._lock:
            if task_id not in self._queues:
                self._queues[task_id] = []
            self._queues[task_id].append(queue)
            # Replay existing events
            for event in self._events.get(task_id, []):
                await queue.put(event)

        try:
            while True:
                event = await queue.get()
                if event is None:
                    break
                yield event
                if event.event == StreamEventType.DONE:
                    break
        finally:
            async with self._lock:
                if task_id in self._queues and queue in self._queues[task_id]:
                    self._queues[task_id].remove(queue)

    async def close_stream(self, task_id: str):
        """Signal all subscribers that the stream is done."""
        async with self._lock:
            for queue in self._queues.get(task_id, []):
                await queue.put(None)


# Singleton
task_store = TaskStore()
