from __future__ import annotations

import logging
from typing import Any

from app.trading.broker_gateway.alpaca_paper import AlpacaPaperBroker
from app.trading.config import get_settings
from app.trading.decision_engine.service import DecisionEngine
from app.trading.logging_config import setup_logging
from app.trading.market_data.alpaca_client import AlpacaMarketDataClient
from app.trading.persistence.db import init_db
from app.trading.persistence.repositories import TradingRepository
from app.trading.risk_manager.service import PortfolioContext, RiskManager
from app.trading.schemas import OrderRequest
from app.trading.signals.signal_service import SignalService

logger = logging.getLogger(__name__)


def run_pipeline() -> dict[str, Any]:
    settings = get_settings()
    session_factory = init_db(settings.database_url)
    market_client = AlpacaMarketDataClient(settings)
    signal_service = SignalService()
    decision_engine = DecisionEngine()
    risk_manager = RiskManager(settings)
    broker = AlpacaPaperBroker(settings)

    with session_factory() as session:
        repo = TradingRepository(session)
        account = broker.get_account()
        equity = float(account.get("equity", settings.starting_capital))
        day_start_equity = repo.get_latest_equity_today() or settings.starting_capital
        run = repo.create_run(equity=equity)

        broker_positions = broker.list_positions()
        repo.replace_positions(broker_positions)

        summary: dict[str, Any] = {"run_id": run.id, "decisions": []}
        for ticker in settings.tickers:
            candles = market_client.fetch_5min_bars(ticker=ticker, limit=250)
            repo.save_market_snapshot(run.id, ticker, candles)

            signal = signal_service.compute(ticker, candles)
            repo.save_signal(run.id, signal)

            decision = decision_engine.decide(signal)
            risk = risk_manager.validate(
                decision,
                PortfolioContext(
                    equity=equity,
                    open_positions=broker_positions,
                    day_start_equity=day_start_equity,
                ),
            )
            decision.risk_check = {"allowed": risk.allowed, "reasons": risk.reasons, **risk.details}
            repo.save_decision(run.id, decision)

            if risk.allowed and decision.action in {"BUY", "SELL"}:
                side = "buy" if decision.action == "BUY" else "sell"
                order = OrderRequest(ticker=ticker, side=side, notional=equity * settings.max_risk_per_trade)
                order_result = broker.place_order(order)
                repo.save_order(
                    run.id,
                    ticker=ticker,
                    side=side,
                    qty=order.qty,
                    notional=order.notional,
                    status=str(order_result.get("status", "submitted")),
                    payload=order_result,
                )
            else:
                repo.save_order(
                    run.id,
                    ticker=ticker,
                    side="none",
                    qty=None,
                    notional=None,
                    status="skipped",
                    payload={"reason": "; ".join(risk.reasons)},
                )

            logger.info(
                "Decision generated",
                extra={"ticker": ticker, "action": decision.action, "run_id": run.id},
            )
            summary["decisions"].append(decision.model_dump())

        repo.finish_run(run.id, status="completed", equity=equity, metadata=summary)
        logger.info("Run complete", extra={"run_id": run.id})
        return summary


def main() -> None:
    setup_logging()
    run_pipeline()


if __name__ == "__main__":
    main()
