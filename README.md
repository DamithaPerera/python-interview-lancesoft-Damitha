# Money Changer Web API (FastAPI)

## Overview
This project implements a money changer backend API with:
- daily exchange rates (`BUY` / `SELL`)
- quote generation before transaction commit
- transaction snapshot storage (effective rate at execution time)
- no customer PII storage

It follows a layered structure:
- `routers` (HTTP route mapping)
- `controllers` (request/response orchestration)
- `services/business` (domain logic)
- `repositories` (data access)
- `models` / `schemas` (ORM + API contracts)

## Key Business Rules
- Exchange rates are daily and unique by:
  - `rate_date`
  - `base_currency`
  - `quote_currency`
  - `side`
- Transactions use the daily rate from `timestamp.date()`.
- Exactly one of `foreign_amount` or `base_amount` must be provided.
- The transaction stores `effective_rate` as a snapshot.
- Customer details are not stored.

## API Flow
Recommended flow:
1. Create daily rate(s).
2. Generate quote with `POST /quotes`.
3. Confirm quote with `POST /transactions/confirm` to persist transaction.

Direct flow (still supported):
- `POST /transactions` computes and persists in one step.

## Endpoints
### Rates
- `POST /rates`
  - create daily rate
  - returns `409` if same composite key already exists
- `GET /rates`
  - list/filter by optional query params: `rate_date`, `base_currency`, `quote_currency`, `side`
- `GET /rates/{rate_date}/{base_currency}/{quote_currency}/{side}`
  - fetch a single rate by composite key
- `PUT /rates/{rate_date}/{base_currency}/{quote_currency}/{side}`
  - update existing rate
- `DELETE /rates/{rate_date}/{base_currency}/{quote_currency}/{side}`
  - delete existing rate

### Quotes
- `POST /quotes`
  - calculates and stores a quote
  - returns `quote_id`, computed amounts, `effective_rate`, `expires_at`
  - returns `422` for invalid payload or missing daily rate

### Transactions
- `POST /transactions`
  - direct one-step create (calculate + persist)
- `POST /transactions/confirm`
  - confirm previously created quote
  - request body: `{ "quote_id": "QTE-..." }`
  - returns:
    - `200` on success
    - `404` if quote not found
    - `409` if quote already confirmed
    - `422` if quote expired

## Local Setup
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

On macOS/Linux, use:
```bash
cp .env.example .env
```

Docs:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Docker
### Build and run
```bash
docker build -t money-changer-api .
docker run --rm -p 8000:8000 --env-file .env money-changer-api
```

### Docker Compose
```bash
docker compose up --build
```

### Notes
- Container startup runs migration bootstrap via `docker/entrypoint.sh`:
  - handles legacy SQLite schema state
  - runs Alembic migration/stamp as needed
  - starts Uvicorn

## Environment Variables
See `.env.example`.

Main variables:
- `DATABASE_URL` (default: `sqlite:///./fx.db`)
- `QUOTE_TTL_MINUTES` (default: `15`)
- `BUY_SPREAD_BPS` (default: `0`)
- `SELL_SPREAD_BPS` (default: `0`)
- `FEE_PERCENT` (default: `0`)

## Testing
```bash
pytest -q
```

Current suite covers:
- all API endpoints (happy path + key error paths)
- uniqueness and key-route behavior for rates
- quote/confirm lifecycle
- BUY vs SELL calculator behavior
- repository-level operations and config sanity
