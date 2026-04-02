from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


AgentName = Literal["product", "legal", "marketing", "design", "development", "qa"]
TaskStatus = Literal["planned", "in_progress", "completed"]


class AgentSpec(BaseModel):
    name: str
    purpose: str
    automated: bool = True


class MissionTaskCreate(BaseModel):
    idea: str = Field(min_length=5)
    scope: str = Field(min_length=5)


class MissionTask(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    idea: str
    scope: str
    status: TaskStatus = "planned"


class AgentWorkItem(BaseModel):
    task_id: str
    agent: str
    objective: str
    status: TaskStatus = "planned"
    output: str = ""


class TaskExecutionResult(BaseModel):
    task: MissionTask
    work_items: list[AgentWorkItem]
