from __future__ import annotations

from app.mission_control.models import MissionTaskCreate
from app.mission_control.orchestrator import MissionOrchestrator


def test_default_agents_are_present() -> None:
    orchestrator = MissionOrchestrator()
    names = {a.name for a in orchestrator.list_agents()}
    assert {"product", "legal", "marketing", "design", "development", "qa"}.issubset(names)


def test_planning_adds_ollama_work_when_scope_mentions_cloud() -> None:
    orchestrator = MissionOrchestrator()
    task = orchestrator.create_task(MissionTaskCreate(idea="Mission Control", scope="private cloud with ollama"))
    work = orchestrator.work[task.id]
    objectives = [w.objective.lower() for w in work]
    assert any("ollama" in objective for objective in objectives)


def test_execute_task_completes_all_work_items() -> None:
    orchestrator = MissionOrchestrator()
    task = orchestrator.create_task(MissionTaskCreate(idea="Mission Control", scope="full product lifecycle"))
    result = orchestrator.execute_task(task.id)
    assert result.task.status == "completed"
    assert all(item.status == "completed" for item in result.work_items)
    assert all(item.output for item in result.work_items)
