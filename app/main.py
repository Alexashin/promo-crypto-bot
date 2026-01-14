import asyncio
import logging

from app.bot import build_bot, build_dispatcher
from app.db.session import init_engine
from app.db.seed import ensure_settings_row

from app.logging_config import setup_logging
from app.db.migrate import run_migrations

setup_logging(level="INFO", keep_files=5)

logger = logging.getLogger(__name__)


async def on_startup() -> None:
    run_migrations()
    # Подключаемся к БД и создаём дефолтные настройки (1 строка)
    await init_engine()
    await ensure_settings_row()
    logging.info("Startup OK")


async def main() -> None:
    bot = build_bot()
    dp = build_dispatcher()

    await on_startup()

    logging.info("Bot is running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
