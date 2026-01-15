from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


BTN_PODCAST = "🎧 Получить подкаст"
BTN_ABOUT = "ℹ️ Узнать о соцсети"
BTN_CONSULT = "👤 Получить консультацию"
BTN_REGISTER = "✅ Зарегистрироваться"


def user_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(
        KeyboardButton(text=BTN_PODCAST),
        KeyboardButton(text=BTN_ABOUT),
    )
    kb.add(
        KeyboardButton(text=BTN_CONSULT),
        KeyboardButton(text=BTN_REGISTER),
    )
    return kb.adjust(2).as_markup(resize_keyboard=True, selective=True)  # type: ignore
