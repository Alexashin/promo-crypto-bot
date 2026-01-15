from __future__ import annotations

from aiogram.fsm.state import StatesGroup, State


class AdminTemplatesSG(StatesGroup):
    waiting_text = State()
    waiting_media = State()
