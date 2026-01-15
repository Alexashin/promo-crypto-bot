from __future__ import annotations

from app.keyboards.inline import build_inline


def templates_root_kb() -> object:
    return build_inline(
        [
            {"text": "📃 Список шаблонов", "callback": "adm:tpl:list"},
            {"text": "◀️ Назад", "callback": "adm:back"},
        ]
    )


def templates_list_kb(keys: list[str]) -> object:
    rows: list[dict] = [
        {"text": f"📝 {k}", "callback": f"adm:tpl:open:{k}"} for k in keys
    ]
    rows.append({"text": "◀️ Назад", "callback": "adm:set:root"})  # назад в настройки
    return build_inline(rows)


def template_card_kb(key: str, is_active: bool, has_media: bool) -> object:
    rows = [
        {"text": "✏️ Изменить текст", "callback": f"adm:tpl:edit_text:{key}"},
        {"text": "📎 Прикрепить медиа", "callback": f"adm:tpl:attach:{key}"},
    ]
    if has_media:
        rows.append(
            {"text": "🧹 Удалить медиа", "callback": f"adm:tpl:clear_media:{key}"}
        )

    rows.extend(
        [
            {
                "text": ("🔴 Выключить" if is_active else "🟢 Включить"),
                "callback": f"adm:tpl:toggle:{key}",
            },
            {"text": "📤 Отправить себе (тест)", "callback": f"adm:tpl:test:{key}"},
            {"text": "◀️ К списку", "callback": "adm:tpl:list"},
        ]
    )
    return build_inline(rows)
