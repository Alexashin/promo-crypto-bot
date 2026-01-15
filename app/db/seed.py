from __future__ import annotations

from sqlalchemy import select

from app.config import settings
from app.db.session import SessionFactory
from app.db.models import Setting, PostTemplate, MediaType


DEFAULT_TEMPLATES: list[dict] = [
    # ----- SYSTEM -----
    {
        "key": "welcome",
        "text": "Привет! 👋\n\nЧтобы получить подкаст, подпишись на канал и нажми «Проверить подписку».",
        "media_type": None,
        "file_id": None,
        "buttons": [
            {"text": "📢 Перейти в канал", "url": getattr(settings, "channel_url", "")},
            {"text": "✅ Проверить подписку", "callback": "check_sub"},
        ],
    },
    {
        "key": "not_subscribed",
        "text": "Похоже, ты ещё не подписан(а). Подпишись на канал и нажми «Проверить подписку».",
        "media_type": None,
        "file_id": None,
        "buttons": [
            {"text": "📢 Перейти в канал", "url": getattr(settings, "channel_url", "")},
            {"text": "✅ Проверить подписку", "callback": "check_sub"},
        ],
    },
    {
        "key": "bot_not_in_channel",
        "text": (
            "⚠️ Сейчас я не могу проверить подписку.\n\n"
            "Возможные причины:\n"
            "— меня ещё не добавили в канал\n"
            "— у меня нет прав видеть участников\n\n"
            "👉 Напиши администратору или попробуй позже."
        ),
        "media_type": None,
        "file_id": None,
        "buttons": [
            {
                "text": "📢 Перейти в канал",
                "url": settings.channel_url,
            }
        ],
    },
    # ----- PODCAST (пример, file_id заполни сам реальным voice file_id) -----
    {
        "key": "podcast_1",
        "text": "🎧 Подкаст #1. Приятного прослушивания!",
        "media_type": MediaType.voice,
        "file_id": None,  # <-- вставишь сюда voice file_id
        "buttons": None,
    },
    {
        "key": "menu_after_podcast",
        "text": (
            "Готово ✅ Подкаст у тебя.\n\n"
            "Дальше выбери, что нужно:\n"
            "🎧 Получить подкаст ещё раз\n"
            "ℹ️ Узнать о соцсети\n"
            "👤 Получить консультацию\n"
            "✅ Зарегистрироваться (и отключить напоминания)\n"
        ),
        "media_type": None,
        "file_id": None,
        "buttons": None,
    },
    {
        "key": "social_info_1",
        "text": "ℹ️ (Заглушка) Тут будет информация о соцсети + ссылка.",
        "media_type": None,
        "file_id": None,
        "buttons": [
            {"text": "Перейти в соцсеть", "url": "https://example.com"},
            {"text": "Получить консультацию", "callback": "consult"},
        ],
    },
    {
        "key": "consult_info",
        "text": "👤 (Заглушка) Тут будет описание консультации.",
        "media_type": None,
        "file_id": None,
        "buttons": [
            {"text": "Написать Юрию", "url": "https://t.me/example"},
        ],
    },
    {
        "key": "register_instructions",
        "text": "✅ (Заглушка) Тут будет инструкция по регистрации + ссылка.",
        "media_type": None,
        "file_id": None,
        "buttons": [
            {"text": "Перейти в соцсеть", "url": "https://example.com"},
            {"text": "Я зарегистрировался", "callback": "registered"},
        ],
    },
    # ----- REMINDERS -----
    {
        "key": "reminder_1",
        "text": "Напоминание #1: подкаст ждёт 🙂 Если ты уже зарегистрировался — нажми кнопку ниже.",
        "media_type": None,
        "file_id": None,
        "buttons": [
            {"text": "✅ Я зарегистрировался", "callback": "registered"},
            {"text": "🎧 Получить подкаст", "callback": "get_podcast"},
        ],
    },
    {
        "key": "reminder_2",
        "text": "Напоминание #2: если нужна помощь — можно получить консультацию.",
        "media_type": None,
        "file_id": None,
        "buttons": [
            {"text": "👤 Получить консультацию", "callback": "consult"},
            {"text": "✅ Я зарегистрировался", "callback": "registered"},
        ],
    },
    {
        "key": "reminder_3",
        "text": "Напоминание #3: регистрация занимает пару минут. Если уже сделал — отметься 👇",
        "media_type": None,
        "file_id": None,
        "buttons": [
            {"text": "✅ Я зарегистрировался", "callback": "registered"},
        ],
    },
    {
        "key": "reminder_4",
        "text": "Напоминание #4: могу подсказать шаги регистрации или дать консультацию.",
        "media_type": None,
        "file_id": None,
        "buttons": [
            {"text": "👤 Получить консультацию", "callback": "consult"},
            {"text": "✅ Я зарегистрировался", "callback": "registered"},
        ],
    },
    {
        "key": "reminder_5",
        "text": "Последнее напоминание: если актуально — жми регистрацию. Если нет — всё ок 🙂",
        "media_type": None,
        "file_id": None,
        "buttons": [
            {"text": "✅ Я зарегистрировался", "callback": "registered"},
        ],
    },
]


DEFAULT_SETTINGS = {
    "inactive_hours": str(settings.default_inactive_hours),
    "max_reminders": str(settings.default_max_reminders),
    # берём из ENV, если задано, иначе дефолты
    "channel_id": str(getattr(settings, "channel_id", "") or ""),
    "channel_url": str(
        getattr(settings, "channel_url", "") or "https://t.me/test_channel"
    ),
    "social_url": str(getattr(settings, "social_url", "") or "https://example.com"),
    "consult_contact_name": str(
        getattr(settings, "consult_contact_name", "") or "Юрий"
    ),
    "consult_contact_url": str(
        getattr(settings, "consult_contact_url", "") or "https://t.me/example"
    ),
}


async def seed_settings() -> None:
    async with SessionFactory() as session:
        for k, v in DEFAULT_SETTINGS.items():
            row = await session.get(Setting, k)
            if row is None:
                session.add(Setting(key=k, value=v))
        await session.commit()


async def seed_templates() -> None:
    async with SessionFactory() as session:
        for tpl in DEFAULT_TEMPLATES:
            await _ensure_template(session, tpl)
        await session.commit()


async def run_seed() -> None:
    await seed_settings()
    await seed_templates()


# ----------------- helpers -----------------


async def _ensure_setting(session, key: str, value: str) -> None:
    row = await session.get(Setting, key)
    if row is None:
        session.add(Setting(key=key, value=value))


async def _ensure_template(session, tpl: dict) -> None:
    res = await session.execute(
        select(PostTemplate).where(PostTemplate.key == tpl["key"])
    )
    existing = res.scalar_one_or_none()
    if existing is None:
        session.add(PostTemplate(**tpl))
