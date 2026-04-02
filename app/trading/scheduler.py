from __future__ import annotations

import logging
import time

from app.trading.config import get_settings
from app.trading.logging_config import setup_logging
from app.trading.run_once import run_pipeline

logger = logging.getLogger(__name__)


def main() -> None:
    setup_logging()
    settings = get_settings()
    interval_seconds = settings.trading_interval_minutes * 60
    logger.info("Scheduler started")

    while True:
        try:
            run_pipeline()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Scheduler cycle failed: %s", exc)
        time.sleep(interval_seconds)


if __name__ == "__main__":
    main()
