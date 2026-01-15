from __future__ import annotations

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup
from sqlalchemy import select

from app.db.session import session_scope
from app.db.models import PostTemplate, MediaType
from app.keyboards.inline import build_inline_from_buttons


class PostNotFound(Exception):
    pass


async def get_template(key: str) -> PostTemplate:
    async with session_scope() as session:
        res = await session.execute(
            select(PostTemplate).where(
                PostTemplate.key == key, PostTemplate.is_active == True
            )
        )
        tpl = res.scalar_one_or_none()
        if not tpl:
            raise PostNotFound(f"PostTemplate not found: {key}")
        return tpl


async def send_template(bot: Bot, user_id: int, key: str) -> None:
    tpl = await get_template(key)
    kb: InlineKeyboardMarkup | None = build_inline_from_buttons(tpl.buttons)

    # Нет медиа -> обычный текст
    if tpl.media_type is None or not tpl.file_id:
        if tpl.text:
            await bot.send_message(user_id, tpl.text, reply_markup=kb)
        else:
            # пустой template — лучше не молчать, но и не падать
            await bot.send_message(
                user_id, "⚠️ Контент временно недоступен.", reply_markup=kb
            )
        return

    # Медиа + (опционально) caption
    if tpl.media_type == MediaType.voice:
        await bot.send_voice(user_id, tpl.file_id, caption=tpl.text, reply_markup=kb)
        return

    if tpl.media_type == MediaType.photo:
        await bot.send_photo(user_id, tpl.file_id, caption=tpl.text, reply_markup=kb)
        return

    if tpl.media_type == MediaType.video:
        await bot.send_video(user_id, tpl.file_id, caption=tpl.text, reply_markup=kb)
        return

    if tpl.media_type == MediaType.document:
        await bot.send_document(user_id, tpl.file_id, caption=tpl.text, reply_markup=kb)
        return

    if tpl.media_type == MediaType.video_note:
        # video_note не поддерживает caption/клавиатуру "как обычно"
        await bot.send_video_note(user_id, tpl.file_id)
        if tpl.text or kb:
            await bot.send_message(user_id, tpl.text or "", reply_markup=kb)
        return

    # На всякий случай (если в БД появится новый тип)
    await bot.send_message(
        user_id, tpl.text or "⚠️ Неизвестный тип контента.", reply_markup=kb
    )
