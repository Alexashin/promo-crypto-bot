import logging
import subprocess

logger = logging.getLogger(__name__)


def run_migrations() -> None:
    """
    Запускаем alembic upgrade head внутри контейнера при старте.
    Если миграции уже накатаны — будет no-op.
    """
    logger.info("Running migrations: alembic upgrade head")
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    logger.info("Migrations OK")
