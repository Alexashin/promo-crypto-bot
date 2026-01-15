from __future__ import annotations

from datetime import datetime, timezone

from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.db.models import User
from app.keyboards.reply import user_menu_kb
from app.services.posts import send_template
from app.services.tg_subscribe import is_user_subscribed, SubscribeCheckError
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.tg_subscribe import (
    is_user_subscribed,
    SubscribeCheckError,
)

router = Router()


def _utcnow_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


@router.callback_query(F.data == "check_sub")
async def cb_check_sub(
    call: CallbackQuery, session: AsyncSession, db_user: User
) -> None:
    user_id = call.from_user.id
    try:
        subscribed = await is_user_subscribed(call.bot, session, user_id)
    except SubscribeCheckError:
        await send_template(call.bot, user_id, "bot_not_in_channel")
        await call.answer()
        return

    db_user.is_subscribed = subscribed

    if not subscribed:
        await send_template(call.bot, user_id, "not_subscribed")
        await call.answer()
        return

    # подписан
    await send_template(call.bot, user_id, "podcast_1")
    await send_template(call.bot, user_id, "menu_after_podcast")
    await call.bot.send_message(
        user_id,
        "Выбери действие из меню 👇",
        reply_markup=user_menu_kb(),
    )

    await call.answer()


@router.callback_query(F.data == "registered")
async def cb_registered(call: CallbackQuery, db_user: User) -> None:
    db_user.is_registered = True
    db_user.registered_at = _utcnow_naive()

    await call.message.answer("✅ Принято! Спасибо 🙂 Напоминания отключены.")
    await call.answer()


@router.callback_query(F.data == "get_podcast")
async def cb_get_podcast(call: CallbackQuery, db_user: User) -> None:
    if not db_user.is_subscribed:
        await send_template(call.bot, call.from_user.id, "not_subscribed")
    else:
        await send_template(call.bot, call.from_user.id, "podcast_1")
    await call.answer()
