from __future__ import annotations

from datetime import datetime, timedelta, timezone

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import User, Setting
from app.db.session import SessionFactory
from app.services.posts import send_template


def _utcnow_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def _get_int_setting(session: AsyncSession, key: str, default: int) -> int:
    row = await session.get(Setting, key)
    if row is None or row.value is None or str(row.value).strip() == "":
        return default
    try:
        return int(row.value)
    except ValueError:
        return default


async def reminders_job(bot: Bot) -> None:
    now = _utcnow_naive()

    async with SessionFactory() as session:
        inactive_hours = await _get_int_setting(
            session, "inactive_hours", settings.default_inactive_hours
        )
        max_reminders = await _get_int_setting(
            session, "max_reminders", settings.default_max_reminders
        )

        cutoff = now - timedelta(hours=inactive_hours)

        q = (
            select(User)
            .where(
                and_(
                    User.is_registered.is_(False),
                    User.is_blocked.is_(False),
                    User.reminder_step < max_reminders,
                    User.last_activity_at <= cutoff,
                )
            )
            .limit(200)  # чтобы не убить бота, если юзеров много
        )

        res = await session.execute(q)
        users = res.scalars().all()

        for u in users:
            next_step = u.reminder_step + 1
            key = f"reminder_{next_step}"

            try:
                await send_template(bot, u.tg_id, key)
                u.reminder_step = next_step
                u.last_reminder_at = now
            except TelegramForbiddenError:
                # пользователь заблокировал бота
                u.is_blocked = True

        await session.commit()
