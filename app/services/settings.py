from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Setting
from app.config import settings


async def get_setting(session: AsyncSession, key: str) -> str | None:
    row = await session.get(Setting, key)
    return row.value if row and row.value is not None else None


async def set_setting(session: AsyncSession, key: str, value: str) -> None:
    row = await session.get(Setting, key)
    if row is None:
        session.add(Setting(key=key, value=value))
    else:
        row.value = value


async def get_int_setting(session: AsyncSession, key: str, default: int) -> int:
    raw = await get_setting(session, key)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


async def get_channel_ref(session: AsyncSession) -> int | str | None:
    """
    Возвращает:
      - int  (например -100123...)
      - str  (например '@my_channel')
      - None если не настроено/мусор
    Поддерживаем значения:
      - -1001234567890
      - @my_channel
      - https://t.me/my_channel  (превратим в @my_channel)
      - t.me/my_channel         (превратим в @my_channel)
    """
    raw = (await get_setting(session, "channel_id") or "").strip()
    if not raw:
        return None

    # если дали ссылку — вытащим username
    if "t.me/" in raw:
        raw = raw.split("t.me/", 1)[1].strip()
        raw = raw.split("?", 1)[0].strip()
        raw = raw.split("/", 1)[0].strip()
        raw = "@" + raw.lstrip("@")

    # username канала
    if raw.startswith("@"):
        # Telegram usernames: только [a-zA-Z0-9_], но валидировать строго не обязательно
        return raw

    # числовой id
    try:
        return int(raw)
    except ValueError:
        return None


async def get_channel_url(session: AsyncSession) -> str | None:
    raw = await get_setting(session, "channel_url")
    if raw:
        return raw
    return getattr(settings, "channel_url", None)  # type: ignore
