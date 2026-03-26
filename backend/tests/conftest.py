"""Shared test fixtures."""

from __future__ import annotations

import os

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app
from app.services.task_store import task_store


requires_api_key = pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set",
)


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
def _reset_task_store():
    """Reset the task store between tests."""
    task_store._tasks.clear()
    task_store._events.clear()
    task_store._queues.clear()
