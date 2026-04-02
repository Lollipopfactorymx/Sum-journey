from __future__ import annotations

from fastapi import FastAPI, Header, HTTPException

from app.mission_control.config import get_mission_control_settings
from app.mission_control.models import MissionTask, MissionTaskCreate, TaskExecutionResult
from app.mission_control.orchestrator import MissionOrchestrator
from app.mission_control.storage import MissionStorage

app = FastAPI(title="Mission Control", version="0.2.0")
settings = get_mission_control_settings()
storage = MissionStorage(settings.db_path)
orchestrator = MissionOrchestrator(storage=storage)


def _require_api_key(x_api_key: str | None) -> None:
    if not settings.api_key:
        return
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/agents")
def list_agents(x_api_key: str | None = Header(default=None)):
    _require_api_key(x_api_key)
    return orchestrator.list_agents()


@app.get("/tasks", response_model=list[MissionTask])
def list_tasks(x_api_key: str | None = Header(default=None)):
    _require_api_key(x_api_key)
    return orchestrator.list_tasks()


@app.get("/tasks/{task_id}", response_model=MissionTask)
def get_task(task_id: str, x_api_key: str | None = Header(default=None)):
    _require_api_key(x_api_key)
    try:
        return orchestrator.get_task(task_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Task not found") from exc


@app.post("/tasks", response_model=MissionTask)
def create_task(payload: MissionTaskCreate, x_api_key: str | None = Header(default=None)):
    _require_api_key(x_api_key)
    return orchestrator.create_task(payload)


@app.post("/tasks/{task_id}/execute", response_model=TaskExecutionResult)
def execute_task(task_id: str, x_api_key: str | None = Header(default=None)):
    _require_api_key(x_api_key)
    try:
        return orchestrator.execute_task(task_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Task not found") from exc
