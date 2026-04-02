from __future__ import annotations

from fastapi.testclient import TestClient

from app.mission_control import api


def test_tasks_endpoint_requires_api_key_when_set() -> None:
    original_key = api.settings.api_key
    api.settings.api_key = "secret"
    client = TestClient(api.app)

    unauthorized = client.get("/tasks")
    assert unauthorized.status_code == 401

    authorized = client.get("/tasks", headers={"X-API-Key": "secret"})
    assert authorized.status_code == 200

    api.settings.api_key = original_key
