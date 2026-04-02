from __future__ import annotations

from app.trading.config import get_settings
from app.trading.persistence.db import init_db


def main() -> None:
    settings = get_settings()
    init_db(settings.database_url)
    print(f"Database initialized at: {settings.database_url}")


if __name__ == "__main__":
    main()
