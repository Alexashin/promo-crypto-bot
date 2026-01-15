from aiogram.fsm.state import State, StatesGroup


class AdminSetValueSG(StatesGroup):
    waiting_value = State()


class AdminEditTemplateSG(StatesGroup):
    waiting_text = State()
    waiting_media = State()
