from aiogram import Dispatcher
from aiogram.filters.command import Command

from src.handlers.common.common import (
    cmd_start, cmd_help, cmd_about,
    help_button, about_button, back_to_menu
)
from src.handlers.ai.models import (
    choose_model_type, show_text_models, show_image_models,
    text_model_selected, image_model_selected, update_models_callback
)
from src.handlers.ai.generation import (
    start_image_generation, start_text_generation,
    process_image_prompt, process_text_prompt,
    cancel_action
)
from src.handlers.ai.history import router as history_router
from src.managers.chat_manager import chat_manager
from src.keyboards.keyboards import get_main_keyboard, get_chat_history_keyboard
from src.states.user import UserState

def register_all_handlers(dp: Dispatcher) -> None:
    """
    Регистрация всех обработчиков бота.
    """
    # Регистрация обработчиков общих команд
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_about, Command("about"))
    
    # Регистрация обработчиков кнопок общего меню
    dp.callback_query.register(help_button, lambda c: c.data == "help")
    dp.callback_query.register(about_button, lambda c: c.data == "about")
    dp.callback_query.register(back_to_menu, lambda c: c.data == "back_to_menu")
    
    # Регистрация обработчиков для работы с моделями
    dp.callback_query.register(choose_model_type, lambda c: c.data == "choose_model")
    dp.callback_query.register(show_text_models, lambda c: c.data == "select_text_models")
    dp.callback_query.register(show_image_models, lambda c: c.data == "select_image_models")
    dp.callback_query.register(text_model_selected, lambda c: c.data.startswith("text_model_"))
    dp.callback_query.register(image_model_selected, lambda c: c.data.startswith("image_model_"))
    dp.callback_query.register(update_models_callback, lambda c: c.data == "update_models")
    
    # Регистрация обработчиков для генерации контента
    dp.callback_query.register(start_image_generation, lambda c: c.data == "generate_image")
    dp.callback_query.register(start_text_generation, lambda c: c.data == "generate_text")
    dp.message.register(process_image_prompt, UserState.waiting_for_image_prompt)
    dp.message.register(process_text_prompt, UserState.waiting_for_text_prompt)
    dp.callback_query.register(cancel_action, lambda c: c.data == "cancel")

    # Регистрация обработчиков для работы с историей чата
    dp.include_router(history_router)
