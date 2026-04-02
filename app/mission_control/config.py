from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MissionControlSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    host: str = Field(default="127.0.0.1", alias="MISSION_CONTROL_HOST")
    port: int = Field(default=8000, alias="MISSION_CONTROL_PORT")
    reload: bool = Field(default=False, alias="MISSION_CONTROL_RELOAD")
    api_key: str = Field(default="", alias="MISSION_CONTROL_API_KEY")
    db_path: str = Field(default="mission_control.db", alias="MISSION_CONTROL_DB_PATH")


@lru_cache(maxsize=1)
def get_mission_control_settings() -> MissionControlSettings:
    return MissionControlSettings()
