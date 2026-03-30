# Sum-journey (Local-only Python MVP)

Sum-journey is a **local command-line AI-assisted trading MVP** for US equities using **Alpaca paper trading only**.

## What this MVP does
- Runs locally from the terminal (no frontend, no cloud deployment).
- Pulls 5-minute candles for `SPY`, `QQQ`, `AAPL`.
- Computes indicators: `RSI`, `MACD`, `EMA20`, `EMA50`, `ATR`.
- Produces decision actions: `BUY`, `SELL`, `HOLD`.
- Applies risk controls before any order placement.
- Persists runs, snapshots, signals, decisions, orders, positions to SQLite.
- Supports one-off execution and recurring 5-minute scheduling.

## Project layout
```
app/
  trading/
    config.py
    logging_config.py
    run_once.py
    scheduler.py
    models.py
    schemas.py
    persistence/
      db.py
      repositories.py
    market_data/
      alpaca_client.py
    signals/
      indicators.py
      signal_service.py
    decision_engine/
      service.py
    risk_manager/
      service.py
    broker_gateway/
      alpaca_paper.py

tests/
  test_indicators.py
  test_decision_engine.py
```

## Setup
1. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure env vars**
   ```bash
   cp .env.example .env
   ```
   Fill in:
   - `ALPACA_API_KEY`
   - `ALPACA_SECRET_KEY`

## Environment variables
- `ALPACA_API_KEY=`
- `ALPACA_SECRET_KEY=`
- `ALPACA_BASE_URL=https://paper-api.alpaca.markets`
- `DATABASE_URL=sqlite:///sum_journey.db`
- `TRADING_TICKERS=SPY,QQQ,AAPL`
- `TRADING_TIMEFRAME=5Min`
- `TRADING_INTERVAL_MINUTES=5`
- `STARTING_CAPITAL=100000`
- `ENABLE_ORDER_PLACEMENT=false` (safety default)

## Run once
```bash
python -m app.trading.run_once
```

Pipeline:
1. Read config
2. Fetch latest candles
3. Compute indicators
4. Generate decision
5. Validate risk
6. Optionally place paper order (only if risk allows and placement enabled)
7. Persist results
8. Log summary

## Run scheduler (every 5 minutes)
```bash
python -m app.trading.scheduler
```

- Runs continuously.
- Logs each cycle.
- Exceptions are caught per cycle so the scheduler keeps running.

## Risk controls implemented
- Max risk per trade: **2%** of equity.
- Max exposure per ticker: **10%**.
- Max simultaneous positions: **3**.
- Stop trading when daily drawdown > **3%**.

## Tests
```bash
pytest
```

Includes tests for:
- indicator calculations and expected columns
- decision engine BUY/HOLD behavior

## Important constraints respected
- Paper trading only (Alpaca).
- No live trading mode.
- No frontend app.
- No Docker/Kubernetes/cloud infra.
- Local-only MVP.
