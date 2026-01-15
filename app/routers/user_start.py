from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.services.posts import send_template

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await send_template(message.bot, message.from_user.id, "welcome")
