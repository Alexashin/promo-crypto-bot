from __future__ import annotations

from html import escape

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.config import settings
from app.keyboards.admin_reply import admin_menu_kb
from app.keyboards.admin_templates import (
    templates_list_kb,
    template_card_kb,
    templates_root_kb,
)
from app.services.posts import (
    list_templates,
    get_template,
    set_template_text,
    set_template_media,
    clear_template_media,
    toggle_template_active,
    send_template,
    PostNotFound,
)
from app.states.admin_templates import AdminTemplatesSG
from app.utils.tg_safe import safe_edit_text

router = Router()


def _is_admin(user_id: int) -> bool:
    return user_id in settings.admin_id_set


def _render_template_card_text(
    key: str,
    is_active: bool,
    text: str | None,
    media_type,
    file_id,
) -> str:
    t = (text or "").strip()
    t_preview = t if len(t) <= 500 else (t[:500] + "…")

    mt = "" if media_type is None else str(media_type)
    fid = "" if file_id is None else str(file_id)

    return (
        f"📝 <b>Шаблон</b>: <code>{escape(str(key))}</code>\n"
        f"Статус: {'🟢 активен' if is_active else '🔴 выключен'}\n\n"
        f"<b>Текст</b>:\n{escape(t_preview) if t_preview else '<i>(пусто)</i>'}\n\n"
        f"<b>Медиа</b>:\n"
        f"type: <code>{escape(mt)}</code>\n"
        f"file_id: <code>{escape(fid)}</code>\n"
    )


@router.message(F.text == "📝 Шаблоны")
async def templates_entry(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        return
    await message.answer(
        "📝 Шаблоны: нажми кнопку ниже.", reply_markup=templates_root_kb()
    )


@router.callback_query(F.data == "adm:tpl:list")
async def tpl_list(call: CallbackQuery, session) -> None:
    if not _is_admin(call.from_user.id):
        await call.answer("Нет доступа", show_alert=True)
        return

    templates = await list_templates(session)
    keys = [t.key for t in templates]

    text = "📃 <b>Список шаблонов</b>\n\nВыбери шаблон:"
    kb = templates_list_kb(keys)

    await safe_edit_text(call.message, text, reply_markup=kb, parse_mode="HTML")
    await call.answer()


@router.callback_query(F.data.startswith("adm:tpl:open:"))
async def tpl_open(call: CallbackQuery, session) -> None:
    if not _is_admin(call.from_user.id):
        await call.answer("Нет доступа", show_alert=True)
        return

    key = call.data.split("adm:tpl:open:", 1)[1]

    try:
        tpl = await get_template(session, key)
    except PostNotFound:
        await call.answer("Шаблон не найден", show_alert=True)
        return

    text = _render_template_card_text(
        key=tpl.key,
        is_active=bool(tpl.is_active),
        text=tpl.text,
        media_type=tpl.media_type,
        file_id=tpl.file_id,
    )

    kb = template_card_kb(
        tpl.key, bool(tpl.is_active), bool(tpl.media_type and tpl.file_id)
    )
    await safe_edit_text(call.message, text, reply_markup=kb, parse_mode="HTML")
    await call.answer()


@router.callback_query(F.data.startswith("adm:tpl:edit_text:"))
async def tpl_edit_text(call: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin(call.from_user.id):
        await call.answer("Нет доступа", show_alert=True)
        return

    key = call.data.split("adm:tpl:edit_text:", 1)[1]
    await state.set_state(AdminTemplatesSG.waiting_text)
    await state.update_data(tpl_key=key)

    await call.message.answer(
        f"✏️ Введи новый текст для шаблона <code>{escape(key)}</code>.\n"
        f"Чтобы очистить текст — отправь <code>-</code>",
        parse_mode="HTML",
        reply_markup=admin_menu_kb(),
    )
    await call.answer()


@router.message(AdminTemplatesSG.waiting_text)
async def tpl_save_text(message: Message, state: FSMContext, session) -> None:
    if not _is_admin(message.from_user.id):
        await state.clear()
        return

    data = await state.get_data()
    key = data["tpl_key"]

    raw = (message.text or "").strip()
    new_text = None if raw == "-" else raw

    await set_template_text(session, key, new_text)
    await state.clear()

    await message.answer("✅ Текст сохранён. Открываю карточку шаблона…")

    # покажем карточку
    tpl = await get_template(session, key)
    card = _render_template_card_text(
        key=tpl.key,
        is_active=bool(tpl.is_active),
        text=tpl.text,
        media_type=tpl.media_type,
        file_id=tpl.file_id,
    )
    kb = template_card_kb(
        tpl.key, bool(tpl.is_active), bool(tpl.media_type and tpl.file_id)
    )
    await message.answer(card, parse_mode="HTML", reply_markup=kb)


@router.callback_query(F.data.startswith("adm:tpl:attach:"))
async def tpl_attach_media(call: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin(call.from_user.id):
        await call.answer("Нет доступа", show_alert=True)
        return

    key = call.data.split("adm:tpl:attach:", 1)[1]
    await state.set_state(AdminTemplatesSG.waiting_media)
    await state.update_data(tpl_key=key)

    await call.message.answer(
        "📎 Пришли медиа одним сообщением (voice/photo/video/document/video_note).\n"
        "Чтобы отменить — напиши слово <b>отмена</b>.",
        parse_mode="HTML",
        reply_markup=admin_menu_kb(),
    )
    await call.answer()


@router.message(AdminTemplatesSG.waiting_media)
async def tpl_save_media(message: Message, state: FSMContext, session) -> None:
    if not _is_admin(message.from_user.id):
        await state.clear()
        return

    if (message.text or "").strip().lower() == "отмена":
        await state.clear()
        await message.answer("Ок, отменил.", reply_markup=admin_menu_kb())
        return

    data = await state.get_data()
    key = data["tpl_key"]

    media_type: str | None = None
    file_id: str | None = None

    if message.audio:
        media_type = "audio"
        file_id = message.audio.file_id
    elif message.voice:
        media_type = "voice"
        file_id = message.voice.file_id
    elif message.photo:
        media_type = "photo"
        file_id = message.photo[-1].file_id
    elif message.video:
        media_type = "video"
        file_id = message.video.file_id
    elif message.document:
        media_type = "document"
        file_id = message.document.file_id
    elif message.video_note:
        media_type = "video_note"
        file_id = message.video_note.file_id
    else:
        await message.answer("Пришли аудио/voice/фото/видео/документ.")
        return

    await set_template_media(session, key, media_type, file_id)
    await state.clear()

    await message.answer("✅ Медиа сохранено. Открываю карточку шаблона…")

    tpl = await get_template(session, key)
    card = _render_template_card_text(
        key=tpl.key,
        is_active=bool(tpl.is_active),
        text=tpl.text,
        media_type=tpl.media_type,
        file_id=tpl.file_id,
    )
    kb = template_card_kb(
        tpl.key, bool(tpl.is_active), bool(tpl.media_type and tpl.file_id)
    )
    await message.answer(card, parse_mode="HTML", reply_markup=kb)


@router.callback_query(F.data.startswith("adm:tpl:clear_media:"))
async def tpl_clear_media(call: CallbackQuery, session) -> None:
    if not _is_admin(call.from_user.id):
        await call.answer("Нет доступа", show_alert=True)
        return

    key = call.data.split("adm:tpl:clear_media:", 1)[1]
    await clear_template_media(session, key)
    await call.answer("Медиа удалено ✅")

    tpl = await get_template(session, key)
    text = _render_template_card_text(
        key=tpl.key,
        is_active=bool(tpl.is_active),
        text=tpl.text,
        media_type=tpl.media_type,
        file_id=tpl.file_id,
    )
    kb = template_card_kb(
        tpl.key, bool(tpl.is_active), bool(tpl.media_type and tpl.file_id)
    )
    await safe_edit_text(call.message, text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("adm:tpl:toggle:"))
async def tpl_toggle(call: CallbackQuery, session) -> None:
    if not _is_admin(call.from_user.id):
        await call.answer("Нет доступа", show_alert=True)
        return

    key = call.data.split("adm:tpl:toggle:", 1)[1]
    new_state = await toggle_template_active(session, key)
    await call.answer("Включено ✅" if new_state else "Выключено ✅")

    tpl = await get_template(session, key)
    text = _render_template_card_text(
        key=tpl.key,
        is_active=bool(tpl.is_active),
        text=tpl.text,
        media_type=tpl.media_type,
        file_id=tpl.file_id,
    )
    kb = template_card_kb(
        tpl.key, bool(tpl.is_active), bool(tpl.media_type and tpl.file_id)
    )
    await safe_edit_text(call.message, text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("adm:tpl:test:"))
async def tpl_test_send(call: CallbackQuery, session) -> None:
    if not _is_admin(call.from_user.id):
        await call.answer("Нет доступа", show_alert=True)
        return

    key = call.data.split("adm:tpl:test:", 1)[1]
    try:
        await send_template(call.bot, session, call.from_user.id, key)
    except Exception as e:
        await call.answer(f"Ошибка: {e}", show_alert=True)
        return

    await call.answer("Отправил ✅")
