from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field

Action = Literal["BUY", "SELL", "HOLD"]


class IndicatorSnapshot(BaseModel):
    ticker: str
    timestamp: datetime
    close: float
    ema20: float
    ema50: float
    rsi: float
    macd: float
    macd_signal: float
    atr: float
    macd_crossover: Literal["bullish", "bearish", "none"]
    atr_extreme: bool
    stop_loss_triggered: bool = False
    take_profit_triggered: bool = False


class Decision(BaseModel):
    ticker: str
    timestamp: datetime
    action: Action
    confidence: float = Field(ge=0.0, le=1.0)
    signals: Dict[str, float | str | bool]
    risk_check: Dict[str, str | bool | float]
    reason: str


class RiskResult(BaseModel):
    allowed: bool
    reasons: List[str]
    details: Dict[str, float | int | bool]


class OrderRequest(BaseModel):
    ticker: str
    side: Literal["buy", "sell"]
    qty: Optional[int] = None
    notional: Optional[float] = None
    time_in_force: str = "day"
    order_type: str = "market"
