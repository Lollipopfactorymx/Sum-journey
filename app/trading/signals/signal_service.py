from __future__ import annotations

import pandas as pd

from app.trading.schemas import IndicatorSnapshot
from app.trading.signals.indicators import append_indicators


class SignalService:
    def compute(self, ticker: str, candles_df: pd.DataFrame) -> IndicatorSnapshot:
        df = append_indicators(candles_df)
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest

        bullish_cross = prev["macd"] <= prev["macd_signal"] and latest["macd"] > latest["macd_signal"]
        bearish_cross = prev["macd"] >= prev["macd_signal"] and latest["macd"] < latest["macd_signal"]
        crossover = "bullish" if bullish_cross else "bearish" if bearish_cross else "none"

        atr_threshold = float(df["atr"].tail(100).mean() * 2.0)
        atr_extreme = float(latest["atr"]) > atr_threshold if atr_threshold > 0 else False

        timestamp = latest["timestamp"]
        if hasattr(timestamp, "to_pydatetime"):
            timestamp = timestamp.to_pydatetime()

        return IndicatorSnapshot(
            ticker=ticker,
            timestamp=timestamp,
            close=float(latest["close"]),
            ema20=float(latest["ema20"]),
            ema50=float(latest["ema50"]),
            rsi=float(latest["rsi"]),
            macd=float(latest["macd"]),
            macd_signal=float(latest["macd_signal"]),
            atr=float(latest["atr"]),
            macd_crossover=crossover,
            atr_extreme=atr_extreme,
            stop_loss_triggered=False,
            take_profit_triggered=False,
        )
