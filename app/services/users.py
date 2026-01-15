from __future__ import annotations

from datetime import datetime

from sqlalchemy import select

from app.db.session import session_scope
from app.db.models import User


async def upsert_user(tg_id: int, username: str | None, first_name: str | None) -> User:
    now = datetime.utcnow()

    async with session_scope() as session:
        user = await session.get(User, tg_id)
        if user is None:
            user = User(
                tg_id=tg_id,
                username=username,
                first_name=first_name,
                created_at=now,
                last_activity_at=now,
            )
            session.add(user)
            return user

        # update
        user.username = username
        user.first_name = first_name
        user.last_activity_at = now
        return user


async def touch_activity(tg_id: int) -> None:
    now = datetime.utcnow()
    async with session_scope() as session:
        user = await session.get(User, tg_id)
        if user:
            user.last_activity_at = now
