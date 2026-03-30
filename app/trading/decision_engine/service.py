from __future__ import annotations

from app.trading.schemas import Decision, IndicatorSnapshot


class DecisionEngine:
    def decide(self, signal: IndicatorSnapshot) -> Decision:
        bullish = (
            signal.ema20 > signal.ema50
            and signal.macd_crossover == "bullish"
            and 30 <= signal.rsi <= 60
            and not signal.atr_extreme
        )
        bearish = (
            signal.ema20 < signal.ema50
            and signal.macd_crossover == "bearish"
            and signal.rsi > 70
        )

        if bullish:
            action = "BUY"
            confidence = 0.8
            reason = "Bullish trend + momentum + bounded volatility"
        elif bearish:
            action = "SELL"
            confidence = 0.8
            reason = "Bearish trend + momentum + overbought RSI"
        else:
            action = "HOLD"
            confidence = 0.5
            reason = "No high-quality setup"

        return Decision(
            ticker=signal.ticker,
            timestamp=signal.timestamp,
            action=action,
            confidence=confidence,
            signals={
                "ema20": signal.ema20,
                "ema50": signal.ema50,
                "macd": signal.macd,
                "macd_signal": signal.macd_signal,
                "macd_crossover": signal.macd_crossover,
                "rsi": signal.rsi,
                "atr": signal.atr,
                "atr_extreme": signal.atr_extreme,
            },
            risk_check={},
            reason=reason,
        )
