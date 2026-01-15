from __future__ import annotations

import asyncio
import logging

from app.bot import build_bot
from app.dispatcher import build_dispatcher
from app.logging_config import setup_logging
from app.db.migrate import run_migrations  # оставь как у тебя называется
from app.db.seed import run_seed
from app.scheduler.scheduler import build_scheduler

logger = logging.getLogger(__name__)


async def main() -> None:
    setup_logging(log_dir="logs", level="INFO", keep_files=5, console=True)

    # миграции до старта бота
    run_migrations()  # type: ignore
    await run_seed()

    bot = build_bot()
    dp = build_dispatcher()

    logger.info("Startup OK")
    logger.info("Bot is running...")

    scheduler = build_scheduler(bot, interval_minutes=10)
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
