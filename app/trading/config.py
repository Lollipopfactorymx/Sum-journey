from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    alpaca_api_key: str = Field(default="", alias="ALPACA_API_KEY")
    alpaca_secret_key: str = Field(default="", alias="ALPACA_SECRET_KEY")
    alpaca_base_url: str = Field(default="https://paper-api.alpaca.markets", alias="ALPACA_BASE_URL")

    database_url: str = Field(default="sqlite:///sum_journey.db", alias="DATABASE_URL")
    trading_tickers: str = Field(default="SPY,QQQ,AAPL", alias="TRADING_TICKERS")
    trading_timeframe: str = Field(default="5Min", alias="TRADING_TIMEFRAME")
    trading_interval_minutes: int = Field(default=5, alias="TRADING_INTERVAL_MINUTES")

    starting_capital: float = Field(default=100000.0, alias="STARTING_CAPITAL")
    max_risk_per_trade: float = 0.02
    max_exposure_per_ticker: float = 0.10
    max_simultaneous_positions: int = 3
    max_daily_drawdown: float = 0.03

    enable_order_placement: bool = Field(default=False, alias="ENABLE_ORDER_PLACEMENT")

    @property
    def tickers(self) -> List[str]:
        return [ticker.strip().upper() for ticker in self.trading_tickers.split(",") if ticker.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
