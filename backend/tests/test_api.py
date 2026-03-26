"""API route tests — unit tests don't need a key, integration tests do."""

import pytest

from tests.conftest import requires_api_key


class TestHealthEndpoint:
    async def test_health(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestTaskEndpoints:
    async def test_create_task_validation_error(self, client):
        resp = await client.post("/api/v1/tasks", json={"query": ""})
        assert resp.status_code == 422

    async def test_create_task_missing_field(self, client):
        resp = await client.post("/api/v1/tasks", json={})
        assert resp.status_code == 422

    async def test_get_nonexistent_task(self, client):
        resp = await client.get("/api/v1/tasks/nonexistent-id")
        assert resp.status_code == 404

    async def test_list_tasks_empty(self, client):
        resp = await client.get("/api/v1/tasks")
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_stream_nonexistent_task(self, client):
        resp = await client.get("/api/v1/tasks/nonexistent-id/stream")
        assert resp.status_code == 404


@requires_api_key
class TestIntegrationCreateTask:
    """These tests hit the real Claude API."""

    async def test_create_and_get_task(self, client):
        resp = await client.post(
            "/api/v1/tasks",
            json={"query": "What is 2 + 2? Keep it very short."},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["task_id"]
        assert data["status"] in ("pending", "running")

        # Retrieve it
        resp2 = await client.get(f"/api/v1/tasks/{data['task_id']}")
        assert resp2.status_code == 200
        assert resp2.json()["query"] == "What is 2 + 2? Keep it very short."

    async def test_list_includes_created_task(self, client):
        await client.post(
            "/api/v1/tasks",
            json={"query": "Say hello"},
        )
        resp = await client.get("/api/v1/tasks")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1
