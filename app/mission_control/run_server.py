from __future__ import annotations

import uvicorn

from app.mission_control.config import get_mission_control_settings


def main() -> None:
    settings = get_mission_control_settings()
    uvicorn.run(
        "app.mission_control.api:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )


if __name__ == "__main__":
    main()
