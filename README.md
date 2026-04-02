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

## Nuevo: Mission Control Web App (agentes)
Se agregó una app web local para coordinar agentes automatizados por rol:
- `product`
- `legal`
- `marketing`
- `design`
- `development`
- `qa`

El orquestador crea tareas, planifica delegación por scope, ejecuta agentes y genera entregables iniciales iterativos.

## Project layout
```
app/
  trading/
    config.py
    logging_config.py
    init_db.py
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
  mission_control/
    test_orchestrator.py
```

## Setup (recommended)
1. **Use Python 3.11+**
   ```bash
   python --version
   ```
2. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. **Upgrade pip and install dependencies**
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. **Configure env vars**
   ```bash
   cp .env.example .env
   ```
   Fill in:
   - `ALPACA_API_KEY`
   - `ALPACA_SECRET_KEY`

## One-command bootstrap (local)
Use the helper script to run the full first-time setup and one cycle:

```bash
bash scripts/bootstrap.sh
```

This script performs:
1. Create virtual environment
2. Install requirements
3. Initialize SQLite database
4. Run a single trading cycle

You can review/edit it at `scripts/bootstrap.sh`.

## Manual bootstrap (exact commands)
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
# edit .env and set ALPACA_API_KEY / ALPACA_SECRET_KEY
python -m app.trading.init_db
python -m app.trading.run_once
```

## Ejecutar Mission Control (web local)
```bash
source .venv/bin/activate
python -m app.mission_control.run_server
```

API local disponible en `http://127.0.0.1:8000`.

### Configuración recomendada para Mission Control
En tu `.env` agrega:
```env
MISSION_CONTROL_HOST=127.0.0.1
MISSION_CONTROL_PORT=8000
MISSION_CONTROL_RELOAD=false
MISSION_CONTROL_API_KEY=
MISSION_CONTROL_DB_PATH=mission_control.db
```

- `MISSION_CONTROL_API_KEY` vacío: API abierta en local.
- `MISSION_CONTROL_API_KEY` con valor: requiere `X-API-Key`.
- `MISSION_CONTROL_DB_PATH`: guarda tareas/work-items en SQLite (persistencia entre reinicios).

### Endpoints principales
```bash
curl http://127.0.0.1:8000/health
curl -H "X-API-Key: <TU_API_KEY>" http://127.0.0.1:8000/agents
curl -H "X-API-Key: <TU_API_KEY>" http://127.0.0.1:8000/tasks
curl -X POST http://127.0.0.1:8000/tasks \
  -H \"Content-Type: application/json\" -H "X-API-Key: <TU_API_KEY>" \
  -d '{\"idea\":\"Control mission\",\"scope\":\"private cloud ollama automation\"}'
curl -H "X-API-Key: <TU_API_KEY>" http://127.0.0.1:8000/tasks/<TASK_ID>
curl -X POST -H "X-API-Key: <TU_API_KEY>" http://127.0.0.1:8000/tasks/<TASK_ID>/execute
```

## Próximo paso: automatización con Ollama en cloud privado
Plan inicial recomendado:
1. **Aislamiento de red**: VPC privada, sin salida pública directa.
2. **Modelo local**: desplegar Ollama en nodos privados con cifrado en reposo.
3. **Orquestación segura**: el agente `development` enruta prompts sanitizados y registra auditoría.
4. **Gobernanza de datos**: clasificación de datos + policies de redacción de PII.
5. **Observabilidad**: trazas por agente, costos, latencia y quality gates de QA/legal.

## Despliegue web en Cloudflare (Mission Control)
Se agregó una versión web deployable en Cloudflare Workers.

### Archivos de despliegue
- `cloudflare/worker.mjs`
- `wrangler.toml`
- `scripts/deploy_cloudflare.sh`
- `scripts/cloudflare_link_and_deploy.sh`

### Cómo enlazar tu cuenta y crear/desplegar todo en Cloudflare
```bash
# 0) Requisito: Node.js 20+
node --version

# 1) Instalar Wrangler (CLI oficial)
npm install -g wrangler

# 2) Desde la raíz del repo, enlazar la cuenta (abre navegador)
wrangler login

# 3) Verificar que quedó enlazada
wrangler whoami

# 4) Crear/desplegar worker con la config de este repo
wrangler deploy
```

Atajo (hace verify + login si falta + deploy):
```bash
bash scripts/cloudflare_link_and_deploy.sh
```

### Comandos exactos
```bash
# 1) Instalar Wrangler (una sola vez)
npm install -g wrangler

# 2) Login en Cloudflare
wrangler login

# 3) Deploy desde la raíz del repo
bash scripts/cloudflare_link_and_deploy.sh
```

Al finalizar, Cloudflare devuelve la URL pública (`*.workers.dev`).

### Si prefieres token (CI/CD o servidor)
```bash
export CLOUDFLARE_API_TOKEN=<tu_token>
wrangler whoami
wrangler deploy
```
Permisos mínimos recomendados del token:
- `Account: Cloudflare Workers Scripts:Edit`
- `Zone: Workers Routes:Edit` (solo si usarás dominio propio/rutas)

### Endpoints en producción
- `GET /` página web Mission Control
- `GET /api/health`
- `GET /api/agents`
- `GET /api/projects`
- `POST /api/projects`
- `GET /api/projects/:project_id/tasks`
- `POST /api/projects/:project_id/tasks`
- `GET /api/tasks/:id`
- `POST /api/tasks/:id/execute` (avance por paso para visualizar progreso)

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

## Troubleshooting
- If you get import errors, verify your virtual environment is activated and dependencies were installed:
  ```bash
  which python
  pip show pandas SQLAlchemy pydantic
  ```
- Keep `ENABLE_ORDER_PLACEMENT=false` until you confirm logs and risk checks look correct.
