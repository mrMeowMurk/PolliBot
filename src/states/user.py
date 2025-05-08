from aiogram.fsm.state import State, StatesGroup

class UserState(StatesGroup):
    waiting_for_prompt = State()
    waiting_for_image_prompt = State()
    waiting_for_text_prompt = State()
    waiting_for_text_image = State()