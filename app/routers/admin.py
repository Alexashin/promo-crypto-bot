from __future__ import annotations

import csv
import io
from datetime import datetime, timedelta, timezone

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from sqlalchemy import select, func

from app.config import settings
from app.db.models import User
from app.keyboards.admin_reply import admin_menu_kb
from app.services.settings import get_int_setting

router = Router()


def _is_admin(user_id: int) -> bool:
    return user_id in settings.admin_id_set


def _utcnow_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


@router.message(Command("admin"))
async def admin_start(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        await message.answer("⛔ Нет доступа.")
        return
    await message.answer("Админка 👇", reply_markup=admin_menu_kb())


@router.message(F.text == "📊 Статистика")
async def admin_stats(message: Message, session) -> None:
    if not _is_admin(message.from_user.id):
        return

    inactive_hours = await get_int_setting(
        session, "inactive_hours", settings.default_inactive_hours
    )
    cutoff = _utcnow_naive() - timedelta(hours=inactive_hours)

    total = await session.scalar(select(func.count()).select_from(User))
    registered = await session.scalar(
        select(func.count()).select_from(User).where(User.is_registered.is_(True))
    )
    subscribed = await session.scalar(
        select(func.count()).select_from(User).where(User.is_subscribed.is_(True))
    )
    blocked = await session.scalar(
        select(func.count()).select_from(User).where(User.is_blocked.is_(True))
    )
    in_reminders = await session.scalar(
        select(func.count()).select_from(User).where(User.reminder_step > 0)
    )
    inactive = await session.scalar(
        select(func.count()).select_from(User).where(User.last_activity_at <= cutoff)
    )

    text = (
        "📊 Статистика\n\n"
        f"👥 Всего: {total}\n"
        f"✅ Зарегистрированы: {registered}\n"
        f"❌ Не зарегистрированы: {total - registered}\n\n"
        f"📢 Подписаны: {subscribed}\n"
        f"🚫 Не подписаны: {total - subscribed}\n\n"
        f"⏰ В напоминаниях: {in_reminders}\n"
        f"💤 Неактивные > {inactive_hours}ч: {inactive}\n"
        f"⛔ Заблокировали бота: {blocked}\n"
    )
    await message.answer(text, reply_markup=admin_menu_kb())


@router.message(F.text == "⬇️ Выгрузка")
async def admin_export(message: Message, session) -> None:
    if not _is_admin(message.from_user.id):
        return

    res = await session.execute(select(User).order_by(User.created_at.asc()))
    users = res.scalars().all()

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(
        [
            "tg_id",
            "username",
            "first_name",
            "is_subscribed",
            "is_registered",
            "reminder_step",
            "last_activity_at",
            "is_blocked",
        ]
    )
    for u in users:
        w.writerow(
            [
                u.tg_id,
                u.username,
                u.first_name,
                u.is_subscribed,
                u.is_registered,
                u.reminder_step,
                u.last_activity_at,
                u.is_blocked,
            ]
        )

    data = buf.getvalue().encode("utf-8-sig")
    file = BufferedInputFile(data, filename="users.csv")
    await message.answer_document(file, caption="⬇️ Выгрузка users.csv")
