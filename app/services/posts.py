from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from aiogram.exceptions import TelegramBadRequest
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import PostTemplate


class PostNotFound(Exception):
    pass


def _now_naive_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def list_templates(session: AsyncSession) -> list[PostTemplate]:
    res = await session.execute(select(PostTemplate).order_by(PostTemplate.key.asc()))
    return list(res.scalars().all())


async def get_template(session: AsyncSession, key: str) -> PostTemplate:
    res = await session.execute(select(PostTemplate).where(PostTemplate.key == key))
    tpl = res.scalar_one_or_none()
    if tpl is None:
        raise PostNotFound(f"PostTemplate not found: {key}")
    return tpl


async def set_template_text(session: AsyncSession, key: str, text: str | None) -> None:
    tpl = await get_template(session, key)
    tpl.text = text
    tpl.updated_at = _now_naive_utc()


async def set_template_media(
    session: AsyncSession, key: str, media_type: str, file_id: str
) -> None:
    tpl = await get_template(session, key)
    tpl.media_type = media_type
    tpl.file_id = file_id
    tpl.updated_at = _now_naive_utc()


async def clear_template_media(session: AsyncSession, key: str) -> None:
    tpl = await get_template(session, key)
    tpl.media_type = None
    tpl.file_id = None
    tpl.updated_at = _now_naive_utc()


async def toggle_template_active(session: AsyncSession, key: str) -> bool:
    tpl = await get_template(session, key)
    tpl.is_active = not bool(tpl.is_active)
    tpl.updated_at = _now_naive_utc()
    return bool(tpl.is_active)


def _build_buttons_from_json(buttons: Any | None) -> InlineKeyboardMarkup | None:
    """
    buttons ожидаем в формате:
      [{"text": "...", "url": "..."}, {"text": "...", "callback": "..."}]
    Пока в админке не редактируем, но отправка поддерживает.
    """
    if not buttons or not isinstance(buttons, list):
        return None

    rows: list[dict] = []
    for b in buttons:
        if not isinstance(b, dict):
            continue
        text = str(b.get("text", "")).strip()
        url = b.get("url")
        cb = b.get("callback")
        if not text:
            continue
        if url:
            rows.append({"text": text, "url": str(url)})
        elif cb:
            rows.append({"text": text, "callback": str(cb)})

    if not rows:
        return None

    # используем ваш build_inline, чтобы не плодить разметку
    from app.keyboards.inline import build_inline

    return build_inline(rows)  # type: ignore


import logging

logger = logging.getLogger(__name__)


async def send_template(
    bot: Bot, session: AsyncSession, chat_id: int, key: str, **kwargs
) -> None:
    tpl = await get_template(session, key)

    if not tpl.is_active:
        raise PostNotFound(f"Template is inactive: {key}")

    text = tpl.text or ""
    markup = _build_buttons_from_json(tpl.buttons)

    # без медиа
    if not tpl.media_type or not tpl.file_id:
        await bot.send_message(chat_id, text or "(пусто)", reply_markup=markup)
        return

    mt = str(tpl.media_type) if tpl.media_type else None

    # если это enum вида "MediaType.photo" — вытащим хвост
    if mt and "." in mt:
        mt = mt.split(".", 1)[1]

    logger.info(
        "send_template key=%s mt=%r file_id=%s active=%s",
        key,
        mt,
        bool(tpl.file_id),
        bool(tpl.is_active),
    )

    if mt == "voice":
        try:
            await bot.send_voice(
                chat_id, tpl.file_id, caption=text or None, reply_markup=markup
            )
        except TelegramBadRequest as e:
            if "VOICE_MESSAGES_FORBIDDEN" in str(e):
                await bot.send_message(chat_id, text="Невозможно отправить документ")
            else:
                raise
        return
    elif mt == "photo":
        await bot.send_photo(
            chat_id, tpl.file_id, caption=text or None, reply_markup=markup
        )
    elif mt == "video":
        await bot.send_video(
            chat_id, tpl.file_id, caption=text or None, reply_markup=markup
        )
    elif mt == "document":
        await bot.send_document(
            chat_id, tpl.file_id, caption=text or None, reply_markup=markup
        )
    elif mt == "video_note":
        # у video_note нет caption
        await bot.send_video_note(chat_id, tpl.file_id, reply_markup=markup)
        if text:
            await bot.send_message(chat_id, text, reply_markup=markup)
    else:
        # неизвестный тип — отправим просто текст + диагностическое
        await bot.send_message(chat_id, text or "(пусто)", reply_markup=markup)
