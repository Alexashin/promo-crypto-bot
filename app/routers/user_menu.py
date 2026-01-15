from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message

from app.db.models import User
from app.services.posts import send_template

router = Router()


@router.message(F.text == "🎧 Получить подкаст")
async def menu_podcast(message: Message, db_user: User) -> None:
    if not db_user.is_subscribed:
        await send_template(message.bot, message.from_user.id, "not_subscribed")
    else:
        await send_template(message.bot, message.from_user.id, "podcast_1")


@router.message(F.text == "ℹ️ Узнать о соцсети")
async def menu_social(message: Message) -> None:
    await send_template(message.bot, message.from_user.id, "social_info_1")


@router.message(F.text == "👤 Получить консультацию")
async def menu_consult(message: Message) -> None:
    await send_template(message.bot, message.from_user.id, "consult_info")


@router.message(F.text == "✅ Зарегистрироваться")
async def menu_register(message: Message) -> None:
    await send_template(message.bot, message.from_user.id, "register_instructions")
