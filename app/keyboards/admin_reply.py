from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def admin_menu_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="📊 Статистика"))
    kb.add(KeyboardButton(text="⚙️ Настройки"))
    kb.add(KeyboardButton(text="📝 Шаблоны"))
    kb.add(KeyboardButton(text="⬇️ Выгрузка"))
    kb.add(KeyboardButton(text="✉️ Рассылка"))
    kb.adjust(2, 2, 1)
    return kb.as_markup(resize_keyboard=True)
