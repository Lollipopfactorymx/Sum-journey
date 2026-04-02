from __future__ import annotations

from app.mission_control.models import MissionTaskCreate
from app.mission_control.orchestrator import MissionOrchestrator
from app.mission_control.storage import MissionStorage


def test_tasks_are_persisted_between_orchestrator_instances(tmp_path) -> None:
    db_path = tmp_path / "mission_control_test.db"

    first = MissionOrchestrator(storage=MissionStorage(str(db_path)))
    created = first.create_task(MissionTaskCreate(idea="Idea persistente", scope="scope base"))

    second = MissionOrchestrator(storage=MissionStorage(str(db_path)))
    fetched = second.get_task(created.id)

    assert fetched.id == created.id
    assert fetched.idea == "Idea persistente"
