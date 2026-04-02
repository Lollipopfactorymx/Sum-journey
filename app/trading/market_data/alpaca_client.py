from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import pandas as pd
import requests

from app.trading.config import Settings


class AlpacaMarketDataClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.headers = {
            "APCA-API-KEY-ID": settings.alpaca_api_key,
            "APCA-API-SECRET-KEY": settings.alpaca_secret_key,
        }

    def fetch_5min_bars(self, ticker: str, limit: int = 250) -> pd.DataFrame:
        if not self.settings.alpaca_api_key or not self.settings.alpaca_secret_key:
            return self._fallback_data(ticker, limit)

        base = "https://data.alpaca.markets"
        url = f"{base}/v2/stocks/{ticker}/bars"
        params = {
            "timeframe": self.settings.trading_timeframe,
            "limit": limit,
            "adjustment": "raw",
        }
        response = requests.get(url, headers=self.headers, params=params, timeout=15)
        response.raise_for_status()
        payload: Dict[str, Any] = response.json()
        bars = payload.get("bars", [])
        if not bars:
            return self._fallback_data(ticker, limit)

        df = pd.DataFrame(bars)
        df = df.rename(columns={"t": "timestamp", "o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"})
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        return df[["timestamp", "open", "high", "low", "close", "volume"]].copy()

    def _fallback_data(self, ticker: str, limit: int) -> pd.DataFrame:
        now = datetime.now(timezone.utc)
        timestamps = [now - timedelta(minutes=5 * idx) for idx in range(limit)][::-1]
        base_price = {"SPY": 500.0, "QQQ": 430.0, "AAPL": 190.0}.get(ticker, 100.0)
        rows = []
        for i, ts in enumerate(timestamps):
            drift = (i / limit) * 2
            close = base_price + drift
            rows.append(
                {
                    "timestamp": ts,
                    "open": close - 0.3,
                    "high": close + 0.5,
                    "low": close - 0.7,
                    "close": close,
                    "volume": 100000 + i * 10,
                }
            )
        return pd.DataFrame(rows)
