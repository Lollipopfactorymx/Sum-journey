from __future__ import annotations

from dataclasses import dataclass

from app.trading.config import Settings
from app.trading.schemas import Decision, RiskResult


@dataclass
class PortfolioContext:
    equity: float
    open_positions: list[dict]
    day_start_equity: float


class RiskManager:
    def __init__(self, settings: Settings):
        self.settings = settings

    def validate(self, decision: Decision, context: PortfolioContext) -> RiskResult:
        if decision.action == "HOLD":
            return RiskResult(allowed=False, reasons=["HOLD action - no order needed"], details={"allowed": False})

        reasons: list[str] = []
        per_trade_cap = context.equity * self.settings.max_risk_per_trade
        max_ticker_exposure = context.equity * self.settings.max_exposure_per_ticker
        day_drawdown = max(0.0, (context.day_start_equity - context.equity) / max(context.day_start_equity, 1.0))

        if day_drawdown > self.settings.max_daily_drawdown:
            reasons.append("Daily drawdown exceeded 3%")

        if len(context.open_positions) >= self.settings.max_simultaneous_positions and decision.action == "BUY":
            reasons.append("Max simultaneous positions reached")

        existing = next((p for p in context.open_positions if p["ticker"] == decision.ticker), None)
        if existing and float(existing["market_value"]) >= max_ticker_exposure and decision.action == "BUY":
            reasons.append("Ticker exposure exceeds 10% cap")

        allowed = len(reasons) == 0
        if allowed:
            reasons.append("Risk checks passed")

        return RiskResult(
            allowed=allowed,
            reasons=reasons,
            details={
                "per_trade_capital": per_trade_cap,
                "max_ticker_exposure": max_ticker_exposure,
                "open_positions": len(context.open_positions),
                "day_drawdown": day_drawdown,
            },
        )
