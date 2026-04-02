from __future__ import annotations

from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.trading.models import (
    DecisionRecord,
    MarketSnapshot,
    OrderRecord,
    PositionRecord,
    Run,
    SignalRecord,
)
from app.trading.schemas import Decision, IndicatorSnapshot


class TradingRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_run(self, equity: float) -> Run:
        run = Run(started_at=datetime.now(timezone.utc), status="started", equity=equity, metadata_json={})
        self.session.add(run)
        self.session.commit()
        return run

    def finish_run(self, run_id: int, status: str, equity: float, metadata: dict | None = None) -> None:
        run = self.session.get(Run, run_id)
        if not run:
            return
        run.finished_at = datetime.now(timezone.utc)
        run.status = status
        run.equity = equity
        if metadata:
            run.metadata_json = metadata
        self.session.commit()

    def save_market_snapshot(self, run_id: int, ticker: str, candles_df) -> None:
        if candles_df.empty:
            return
        last = candles_df.iloc[-1]
        timestamp = last["timestamp"]
        if hasattr(timestamp, "to_pydatetime"):
            timestamp = timestamp.to_pydatetime()
        row = MarketSnapshot(
            run_id=run_id,
            ticker=ticker,
            timestamp=timestamp,
            open=float(last["open"]),
            high=float(last["high"]),
            low=float(last["low"]),
            close=float(last["close"]),
            volume=float(last["volume"]),
        )
        self.session.add(row)
        self.session.commit()

    def save_signal(self, run_id: int, signal: IndicatorSnapshot) -> None:
        record = SignalRecord(
            run_id=run_id,
            ticker=signal.ticker,
            timestamp=signal.timestamp,
            payload=signal.model_dump(),
        )
        self.session.add(record)
        self.session.commit()

    def save_decision(self, run_id: int, decision: Decision) -> None:
        record = DecisionRecord(
            run_id=run_id,
            ticker=decision.ticker,
            timestamp=decision.timestamp,
            action=decision.action,
            confidence=decision.confidence,
            reason=decision.reason,
            payload=decision.model_dump(),
        )
        self.session.add(record)
        self.session.commit()

    def save_order(self, run_id: int, ticker: str, side: str, qty: float | None, notional: float | None, status: str, payload: dict) -> None:
        record = OrderRecord(
            run_id=run_id,
            ticker=ticker,
            timestamp=datetime.now(timezone.utc),
            side=side,
            qty=qty,
            notional=notional,
            status=status,
            broker_order_id=payload.get("id"),
            payload=payload,
        )
        self.session.add(record)
        self.session.commit()

    def replace_positions(self, positions: Sequence[dict]) -> None:
        now = datetime.now(timezone.utc)
        self.session.query(PositionRecord).delete()
        for pos in positions:
            self.session.add(
                PositionRecord(
                    ticker=pos["ticker"],
                    qty=float(pos["qty"]),
                    market_value=float(pos["market_value"]),
                    avg_entry_price=float(pos.get("avg_entry_price", 0.0)),
                    unrealized_pl=float(pos.get("unrealized_pl", 0.0)),
                    as_of=now,
                    is_open=True,
                )
            )
        self.session.commit()

    def get_open_positions(self) -> list[PositionRecord]:
        return list(self.session.scalars(select(PositionRecord).where(PositionRecord.is_open.is_(True))))

    def get_latest_equity_today(self) -> float | None:
        start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        stmt = select(Run).where(Run.started_at >= start_of_day).order_by(desc(Run.started_at)).limit(1)
        latest = self.session.scalar(stmt)
        return float(latest.equity) if latest else None
