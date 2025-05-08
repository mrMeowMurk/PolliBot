from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from config.config import AVAILABLE_MODELS

def get_main_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="🎨 Генерация изображения", callback_data="generate_image"),
            InlineKeyboardButton(text="📝 Генерация текста", callback_data="generate_text")
        ],
        [
            InlineKeyboardButton(text="🤖 Выбор модели", callback_data="choose_model"),
            InlineKeyboardButton(text="🔄 Обновить модели", callback_data="update_models")
        ],
        [
            InlineKeyboardButton(text="❓ Помощь", callback_data="help"),
            InlineKeyboardButton(text="ℹ️ О боте", callback_data="about")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_models_keyboard(models_data: list, model_type: str = "image") -> InlineKeyboardMarkup:
    keyboard = []
    if model_type == "text":
        for model in models_data:
            name = model.get("name", "N/A")
            description = model.get("description", "Нет описания")
            keyboard.append([
                InlineKeyboardButton(
                    text=f"{name} - {description[:30]}...",
                    callback_data=f"text_model_{name}"
                )
            ])
    else:  # image models
        for model_name in models_data:
            keyboard.append([
                InlineKeyboardButton(
                    text=model_name,
                    callback_data=f"image_model_{model_name}"
                )
            ])
    
    keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_cancel_keyboard() -> InlineKeyboardMarkup:
    keyboard = [[
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"),
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")
    ]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_generation_type_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="🎨 Изображения", callback_data="select_image_models"),
            InlineKeyboardButton(text="📝 Текст", callback_data="select_text_models")
        ],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard) 