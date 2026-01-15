from __future__ import annotations

import logging

from aiogram import Router
from aiogram.types import ErrorEvent

logger = logging.getLogger(__name__)
router = Router()


@router.errors()
async def on_error(event: ErrorEvent) -> None:
    logger.exception("Unhandled error: %r", event.exception)
