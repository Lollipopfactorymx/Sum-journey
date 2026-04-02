from __future__ import annotations

from datetime import datetime, timezone

from app.mission_control.agents import DEFAULT_AGENTS
from app.mission_control.models import AgentSpec, AgentWorkItem, MissionTask, MissionTaskCreate, TaskExecutionResult
from app.mission_control.storage import MissionStorage


class MissionOrchestrator:
    def __init__(self, storage: MissionStorage | None = None) -> None:
        self.storage = storage
        self.tasks: dict[str, MissionTask] = {}
        self.work: dict[str, list[AgentWorkItem]] = {}

    def list_agents(self) -> list[AgentSpec]:
        return [AgentSpec(name=a.name, purpose=a.purpose, automated=True) for a in DEFAULT_AGENTS.values()]

    def create_task(self, payload: MissionTaskCreate) -> MissionTask:
        task = MissionTask(idea=payload.idea, scope=payload.scope)
        work_items = self._plan_work(task)
        self.tasks[task.id] = task
        self.work[task.id] = work_items
        self._save(task.id)
        return task

    def list_tasks(self) -> list[MissionTask]:
        if self.storage:
            return self.storage.list_tasks()
        return list(self.tasks.values())

    def get_task(self, task_id: str) -> MissionTask:
        if task_id in self.tasks:
            return self.tasks[task_id]
        if self.storage:
            task = self.storage.get_task(task_id)
            self.tasks[task_id] = task
            self.work[task_id] = self.storage.list_work_items(task_id)
            return task
        raise KeyError(task_id)

    def execute_task(self, task_id: str) -> TaskExecutionResult:
        task = self.get_task(task_id)
        task.status = "in_progress"
        task.updated_at = datetime.now(timezone.utc)

        work_items = self.work[task_id]
        for item in work_items:
            item.status = "in_progress"
            item.output = DEFAULT_AGENTS[item.agent].run(task.idea, item.objective)
            item.status = "completed"

        task.status = "completed"
        task.updated_at = datetime.now(timezone.utc)
        self._save(task_id)
        return TaskExecutionResult(task=task, work_items=work_items)

    def _save(self, task_id: str) -> None:
        if self.storage:
            self.storage.save_task(self.tasks[task_id], self.work[task_id])

    def _plan_work(self, task: MissionTask) -> list[AgentWorkItem]:
        base = [
            AgentWorkItem(task_id=task.id, agent="product", objective="Definir PRD, KPIs y roadmap incremental"),
            AgentWorkItem(task_id=task.id, agent="legal", objective="Evaluar privacidad, compliance y términos"),
            AgentWorkItem(task_id=task.id, agent="marketing", objective="Definir ICP, posicionamiento y GTM"),
            AgentWorkItem(task_id=task.id, agent="design", objective="Diseñar UX de mission control y flujos"),
            AgentWorkItem(task_id=task.id, agent="development", objective="Construir arquitectura y backlog técnico"),
            AgentWorkItem(task_id=task.id, agent="qa", objective="Definir pruebas funcionales y no funcionales"),
        ]
        scope_lower = task.scope.lower()
        if "cloud" in scope_lower or "ollama" in scope_lower:
            base.append(
                AgentWorkItem(
                    task_id=task.id,
                    agent="development",
                    objective="Plan de automatización con Ollama en cloud privado y controles anti-fuga",
                )
            )
        return base
