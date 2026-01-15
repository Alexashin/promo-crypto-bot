# app/middlewares/user_context.py
from __future__ import annotations

from datetime import datetime, timezone

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TgUser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


class UserContextMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        tg_user: TgUser | None = data.get("event_from_user")
        session: AsyncSession = data["session"]

        if tg_user is None:
            return await handler(event, data)

        now = datetime.now(timezone.utc).replace(
            tzinfo=None
        )  # в БД timestamp without tz
        tg_id = tg_user.id

        res = await session.execute(select(User).where(User.tg_id == tg_id))
        user = res.scalar_one_or_none()

        if user is None:
            user = User(
                tg_id=tg_id,
                username=tg_user.username,
                first_name=tg_user.first_name,
                created_at=now,
                last_activity_at=now,
                is_subscribed=False,
                is_registered=False,
                reminder_step=0,
                is_blocked=False,
            )
            session.add(user)
        else:
            user.username = tg_user.username
            user.first_name = tg_user.first_name
            user.last_activity_at = now

        data["db_user"] = user
        return await handler(event, data)
