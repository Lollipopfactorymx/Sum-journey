from __future__ import annotations

from typing import Any

import requests

from app.trading.config import Settings
from app.trading.schemas import OrderRequest


class AlpacaPaperBroker:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = settings.alpaca_base_url
        self.headers = {
            "APCA-API-KEY-ID": settings.alpaca_api_key,
            "APCA-API-SECRET-KEY": settings.alpaca_secret_key,
        }

    def get_account(self) -> dict[str, Any]:
        if not self.settings.alpaca_api_key or not self.settings.alpaca_secret_key:
            return {"equity": str(self.settings.starting_capital)}
        response = requests.get(f"{self.base_url}/v2/account", headers=self.headers, timeout=15)
        response.raise_for_status()
        return response.json()

    def list_positions(self) -> list[dict[str, Any]]:
        if not self.settings.alpaca_api_key or not self.settings.alpaca_secret_key:
            return []
        response = requests.get(f"{self.base_url}/v2/positions", headers=self.headers, timeout=15)
        response.raise_for_status()
        raw = response.json()
        return [
            {
                "ticker": p["symbol"],
                "qty": float(p["qty"]),
                "market_value": float(p["market_value"]),
                "avg_entry_price": float(p["avg_entry_price"]),
                "unrealized_pl": float(p.get("unrealized_pl", 0.0)),
            }
            for p in raw
        ]

    def place_order(self, order: OrderRequest) -> dict[str, Any]:
        if not self.settings.enable_order_placement:
            return {"status": "simulated", "id": "dry-run", "submitted_order": order.model_dump()}
        payload = {
            "symbol": order.ticker,
            "side": order.side,
            "type": order.order_type,
            "time_in_force": order.time_in_force,
        }
        if order.qty is not None:
            payload["qty"] = order.qty
        if order.notional is not None:
            payload["notional"] = order.notional
        response = requests.post(f"{self.base_url}/v2/orders", headers=self.headers, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()
