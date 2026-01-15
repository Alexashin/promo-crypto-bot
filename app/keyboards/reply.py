from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def user_menu_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="🎧 Получить подкаст"))
    kb.add(KeyboardButton(text="ℹ️ Узнать о соцсети"))
    kb.add(KeyboardButton(text="👤 Получить консультацию"))
    kb.add(KeyboardButton(text="✅ Зарегистрироваться"))
    kb.adjust(2, 2)
    return kb.as_markup(resize_keyboard=True)


def admin_menu_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="📊 Статистика"))
    kb.add(KeyboardButton(text="✉️ Рассылка"))
    kb.add(KeyboardButton(text="🕒 Неактивность"))
    kb.add(KeyboardButton(text="⬇️ Выгрузка"))
    kb.adjust(2, 2)
    return kb.as_markup(resize_keyboard=True)
