from __future__ import annotations

from datetime import datetime, timezone

from app.trading.decision_engine.service import DecisionEngine
from app.trading.schemas import IndicatorSnapshot


def test_decision_engine_buy_signal() -> None:
    engine = DecisionEngine()
    signal = IndicatorSnapshot(
        ticker="SPY",
        timestamp=datetime.now(timezone.utc),
        close=500,
        ema20=505,
        ema50=500,
        rsi=50,
        macd=1.2,
        macd_signal=1.0,
        atr=2.0,
        macd_crossover="bullish",
        atr_extreme=False,
    )
    decision = engine.decide(signal)
    assert decision.action == "BUY"


def test_decision_engine_hold_signal() -> None:
    engine = DecisionEngine()
    signal = IndicatorSnapshot(
        ticker="QQQ",
        timestamp=datetime.now(timezone.utc),
        close=400,
        ema20=400,
        ema50=400,
        rsi=65,
        macd=0.1,
        macd_signal=0.2,
        atr=10,
        macd_crossover="none",
        atr_extreme=True,
    )
    decision = engine.decide(signal)
    assert decision.action == "HOLD"
