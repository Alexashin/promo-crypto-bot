# promo-crypto-bot

Telegram bot (aiogram v3 + Postgres + Docker).

## Quick start

1. Copy `.env.example` to `.env` and fill `BOT_TOKEN`.
2. Build & generate first migration:

   ```bash
   docker compose build
   docker compose run --rm bot alembic revision --autogenerate -m "init"
   docker compose up
   ```

The container runs:

- `alembic upgrade head`
- `python -m app.main`
