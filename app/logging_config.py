# app/logging_config.py
from __future__ import annotations

import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


def setup_logging(
    log_dir: str = "logs",
    level: str = "INFO",
    keep_files: int = 5,
    console: bool = True,
) -> None:
    """
    Daily log file rotation. Keeps last N files.
    Creates one file per day: logs/bot.log (+ rotated suffixes).
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Чтобы при перезапуске/реимпорте не плодить хендлеры
    root.handlers.clear()

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Один файл в сутки, хранить последние keep_files
    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_dir, "bot.log"),
        when="midnight",
        interval=1,
        backupCount=keep_files,
        encoding="utf-8",
        utc=True,  # чтобы в контейнере не плясало
    )
    file_handler.setFormatter(fmt)
    file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.addHandler(file_handler)

    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(fmt)
        console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        root.addHandler(console_handler)

    # Подкрутим шумные либы (можешь поменять уровни как хочешь)
    logging.getLogger("aiogram").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)
