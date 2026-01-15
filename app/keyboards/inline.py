from __future__ import annotations

from typing import Any

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def build_inline_from_buttons(
    buttons: list[dict[str, Any]] | None,
) -> InlineKeyboardMarkup | None:
    if not buttons:
        return None

    kb = InlineKeyboardBuilder()
    for b in buttons:
        text = b.get("text")
        if not text:
            continue

        url = b.get("url")
        cb = b.get("callback")

        if url:
            kb.add(InlineKeyboardButton(text=text, url=url))
        elif cb:
            kb.add(InlineKeyboardButton(text=text, callback_data=cb))

    kb.adjust(1)
    return kb.as_markup()


def build_inline(buttons: list[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for b in buttons:
        if b.get("url"):
            kb.button(text=b["text"], url=b["url"])
        else:
            kb.button(text=b["text"], callback_data=b["callback"])
    kb.adjust(1)
    return kb.as_markup()
