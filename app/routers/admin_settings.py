from __future__ import annotations

from html import escape

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.config import settings
from app.keyboards.inline import build_inline
from app.keyboards.admin_reply import admin_menu_kb
from app.states.admin_settings import AdminSetValueSG
from app.services.settings import get_setting, set_setting, get_int_setting
from app.utils.tg_safe import safe_edit_text

router = Router()


def _is_admin(user_id: int) -> bool:
    return user_id in settings.admin_id_set


def _settings_menu_kb():
    return build_inline(
        [
            {"text": "🤖 Бот", "callback": "adm:set:bot"},
            {"text": "⏰ Напоминания", "callback": "adm:set:rem"},
            {"text": "◀️ Назад", "callback": "adm:back"},
        ]
    )


@router.message(F.text == "⚙️ Настройки")
async def settings_root(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        return
    await message.answer("⚙️ Настройки:", reply_markup=_settings_menu_kb())


@router.callback_query(F.data == "adm:back")
async def back(call: CallbackQuery) -> None:
    # safe_edit_text уже гасит "message is not modified"
    await safe_edit_text(call.message, "⚙️ Настройки:", reply_markup=_settings_menu_kb())
    await call.answer()


@router.callback_query(F.data == "adm:set:bot")
async def bot_settings(call: CallbackQuery, session) -> None:
    if not _is_admin(call.from_user.id):
        await call.answer("Нет доступа", show_alert=True)
        return

    channel_id = await get_setting(session, "channel_id") or ""
    channel_url = await get_setting(session, "channel_url") or ""
    social_url = await get_setting(session, "social_url") or ""
    c_name = await get_setting(session, "consult_contact_name") or ""
    c_url = await get_setting(session, "consult_contact_url") or ""

    text = (
        "🤖 <b>Настройки бота</b>\n\n"
        f"channel_id: <code>{escape(channel_id)}</code>\n"
        f"channel_url: {escape(channel_url)}\n"
        f"social_url: {escape(social_url)}\n"
        f"consult_contact_name: {escape(c_name)}\n"
        f"consult_contact_url: {escape(c_url)}\n\n"
        "Выбери, что изменить:"
    )

    kb = build_inline(
        [
            {"text": "✏️ channel_id", "callback": "adm:edit:channel_id"},
            {"text": "✏️ channel_url", "callback": "adm:edit:channel_url"},
            {"text": "✏️ social_url", "callback": "adm:edit:social_url"},
            {
                "text": "✏️ consult_contact_name",
                "callback": "adm:edit:consult_contact_name",
            },
            {
                "text": "✏️ consult_contact_url",
                "callback": "adm:edit:consult_contact_url",
            },
            {"text": "◀️ Назад", "callback": "adm:back"},
        ]
    )

    await safe_edit_text(call.message, text, reply_markup=kb, parse_mode="HTML")
    await call.answer()


@router.callback_query(F.data == "adm:set:rem")
async def reminder_settings(call: CallbackQuery, session) -> None:
    if not _is_admin(call.from_user.id):
        await call.answer("Нет доступа", show_alert=True)
        return

    inactive_hours = await get_int_setting(
        session, "inactive_hours", settings.default_inactive_hours
    )
    max_reminders = await get_int_setting(
        session, "max_reminders", settings.default_max_reminders
    )

    text = (
        "⏰ <b>Напоминания</b>\n\n"
        f"inactive_hours: <code>{escape(str(inactive_hours))}</code>\n"
        f"max_reminders: <code>{escape(str(max_reminders))}</code>\n\n"
        "Выбери, что изменить:"
    )

    kb = build_inline(
        [
            {"text": "✏️ inactive_hours", "callback": "adm:edit:inactive_hours"},
            {"text": "✏️ max_reminders", "callback": "adm:edit:max_reminders"},
            {"text": "◀️ Назад", "callback": "adm:back"},
        ]
    )

    await safe_edit_text(call.message, text, reply_markup=kb, parse_mode="HTML")
    await call.answer()


@router.callback_query(F.data.startswith("adm:edit:"))
async def ask_new_value(call: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin(call.from_user.id):
        await call.answer("Нет доступа", show_alert=True)
        return

    key = call.data.split("adm:edit:", 1)[1]
    await state.set_state(AdminSetValueSG.waiting_value)
    await state.update_data(setting_key=key)

    await call.message.answer(
        f"Введи новое значение для <code>{escape(key)}</code>:",
        parse_mode="HTML",
        reply_markup=admin_menu_kb(),
    )
    await call.answer()


@router.message(AdminSetValueSG.waiting_value)
async def save_new_value(message: Message, state: FSMContext, session) -> None:
    if not _is_admin(message.from_user.id):
        await state.clear()
        return

    data = await state.get_data()
    key = data["setting_key"]
    value = (message.text or "").strip()

    # базовая валидация чисел
    if key in {"inactive_hours", "max_reminders"}:
        if not value.isdigit():
            await message.answer("Нужно число. Попробуй ещё раз.")
            return

    # channel_id тоже число (можно пусто)
    if key == "channel_id":
        if value != "" and not value.lstrip("-").isdigit():
            await message.answer(
                "channel_id должен быть числом (или пусто). Попробуй ещё раз."
            )
            return

    await set_setting(session, key, value)
    await message.answer(
        f"✅ Сохранено: {key} = {value}",
        reply_markup=admin_menu_kb(),
    )
    await state.clear()
