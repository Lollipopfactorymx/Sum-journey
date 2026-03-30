from __future__ import annotations

import pandas as pd

from app.trading.signals.indicators import append_indicators


def _sample_df(rows: int = 120) -> pd.DataFrame:
    data = []
    for i in range(rows):
        close = 100 + i * 0.3
        data.append(
            {
                "timestamp": pd.Timestamp("2025-01-01", tz="UTC") + pd.Timedelta(minutes=5 * i),
                "open": close - 0.2,
                "high": close + 0.5,
                "low": close - 0.7,
                "close": close,
                "volume": 1000 + i,
            }
        )
    return pd.DataFrame(data)


def test_append_indicators_adds_required_columns() -> None:
    df = append_indicators(_sample_df())
    required = {"ema20", "ema50", "rsi", "macd", "macd_signal", "atr"}
    assert required.issubset(df.columns)


def test_ema_trend_direction() -> None:
    df = append_indicators(_sample_df())
    assert float(df.iloc[-1]["ema20"]) > float(df.iloc[-1]["ema50"])
