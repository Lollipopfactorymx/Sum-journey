from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from app.mission_control.models import AgentWorkItem, MissionTask


class MissionStorage:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._ensure_parent_dir()
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_parent_dir(self) -> None:
        parent = Path(self.db_path).expanduser().resolve().parent
        parent.mkdir(parents=True, exist_ok=True)

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS mission_tasks (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    idea TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    status TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS mission_work_items (
                    task_id TEXT NOT NULL,
                    agent TEXT NOT NULL,
                    objective TEXT NOT NULL,
                    status TEXT NOT NULL,
                    output TEXT NOT NULL,
                    PRIMARY KEY (task_id, agent, objective),
                    FOREIGN KEY (task_id) REFERENCES mission_tasks(id)
                )
                """
            )

    def save_task(self, task: MissionTask, work_items: list[AgentWorkItem]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO mission_tasks(id, created_at, updated_at, idea, scope, status)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    updated_at=excluded.updated_at,
                    status=excluded.status,
                    idea=excluded.idea,
                    scope=excluded.scope
                """,
                (
                    task.id,
                    task.created_at.isoformat(),
                    task.updated_at.isoformat(),
                    task.idea,
                    task.scope,
                    task.status,
                ),
            )
            conn.execute("DELETE FROM mission_work_items WHERE task_id = ?", (task.id,))
            conn.executemany(
                """
                INSERT INTO mission_work_items(task_id, agent, objective, status, output)
                VALUES (?, ?, ?, ?, ?)
                """,
                [(item.task_id, item.agent, item.objective, item.status, item.output) for item in work_items],
            )

    def list_tasks(self) -> list[MissionTask]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM mission_tasks ORDER BY created_at DESC").fetchall()
        return [self._row_to_task(dict(row)) for row in rows]

    def get_task(self, task_id: str) -> MissionTask:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM mission_tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            raise KeyError(task_id)
        return self._row_to_task(dict(row))

    def list_work_items(self, task_id: str) -> list[AgentWorkItem]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT task_id, agent, objective, status, output FROM mission_work_items WHERE task_id = ?",
                (task_id,),
            ).fetchall()
        return [AgentWorkItem.model_validate(dict(row)) for row in rows]

    @staticmethod
    def _row_to_task(row: dict[str, Any]) -> MissionTask:
        row["created_at"] = datetime.fromisoformat(row["created_at"])
        row["updated_at"] = datetime.fromisoformat(row["updated_at"])
        return MissionTask.model_validate(row)
