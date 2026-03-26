"""FastAPI routes for task management and SSE streaming."""

from __future__ import annotations

import asyncio
import json
import logging

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from app.schemas.task import (
    StreamEvent,
    StreamEventType,
    SubTask,
    SubTaskResult,
    TaskRequest,
    TaskResponse,
    TaskStatus,
)
from app.services.graph import NexusOrchestrator
from app.services.task_store import task_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1")


@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(request: TaskRequest):
    """Submit a new task for multi-agent processing."""
    task = await task_store.create_task(request.query)

    # Fire off orchestration in background
    asyncio.create_task(_run_orchestration(task.task_id, request.query))

    return task


@router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks():
    """List all tasks, most recent first."""
    return await task_store.list_tasks()


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """Get the current status and results of a task."""
    task = await task_store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/tasks/{task_id}/stream")
async def stream_task(task_id: str):
    """SSE endpoint that streams agent progress events in real time."""
    task = await task_store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    async def event_generator():
        async for event in task_store.subscribe(task_id):
            yield {
                "event": event.event.value,
                "data": json.dumps(event.model_dump(mode="json"), default=str),
            }

    return EventSourceResponse(event_generator())


async def _run_orchestration(task_id: str, query: str):
    """Background task that runs the full orchestration pipeline."""
    await task_store.update_status(task_id, TaskStatus.RUNNING)

    try:
        orchestrator = NexusOrchestrator()
        plan_set = False

        async for event in orchestrator.run(query):
            await task_store.push_event(task_id, event)

            # Update task state based on events
            if event.event == StreamEventType.PLAN and not plan_set:
                try:
                    plan_data = json.loads(event.data)
                    subtasks = [SubTask.model_validate(st) for st in plan_data["subtasks"]]
                    await task_store.set_plan(task_id, subtasks)
                    plan_set = True
                except Exception:
                    logger.exception("Failed to parse plan")

            elif event.event == StreamEventType.AGENT_COMPLETE and event.subtask_id:
                result = SubTaskResult(
                    subtask_id=event.subtask_id,
                    agent=event.agent,
                    status=TaskStatus.COMPLETE,
                    result=event.data,
                )
                await task_store.add_result(task_id, result)

            elif event.event == StreamEventType.ERROR and event.subtask_id:
                result = SubTaskResult(
                    subtask_id=event.subtask_id,
                    agent=event.agent,
                    status=TaskStatus.FAILED,
                    error=event.data,
                )
                await task_store.add_result(task_id, result)

            elif event.event == StreamEventType.DONE:
                await task_store.set_final_answer(task_id, event.data)
                await task_store.update_status(task_id, TaskStatus.COMPLETE)

    except Exception as e:
        logger.exception("Orchestration failed for task %s", task_id)
        error_event = StreamEvent(
            event=StreamEventType.ERROR,
            data=f"Orchestration failed: {e}",
        )
        await task_store.push_event(task_id, error_event)
        await task_store.update_status(task_id, TaskStatus.FAILED)
    finally:
        await task_store.close_stream(task_id)
