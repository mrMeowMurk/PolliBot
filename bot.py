import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramBadRequest

from config.config import BOT_TOKEN, HELP_TEXT, ABOUT_TEXT
from src.keyboards.keyboards import get_main_keyboard, get_models_keyboard, get_cancel_keyboard, get_generation_type_keyboard
from src.utils.pollinations import fetch_all_models, generate_text, generate_image
from src.states.user import UserState

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Состояния FSM


# Хранилище данных пользователей
user_data = {}

def get_user_stats(user_id: int) -> dict:
    """Получение статистики пользователя."""
    if user_id not in user_data:
        user_data[user_id] = {
            "images_generated": 0,
            "texts_generated": 0,
            "last_used": None,
            "current_model": None,
            "model_type": None,
            "text_models": None,
            "image_models": None
        }
    return user_data[user_id]

def get_menu_text(user_id: int) -> str:
    """Формирование текста главного меню с информацией о текущей модели."""
    stats = get_user_stats(user_id)
    current_model = stats.get("current_model", "Не выбрана")
    model_type = stats.get("model_type", "")
    images_count = stats.get("images_generated", 0)
    texts_count = stats.get("texts_generated", 0)

    # Преобразование технического названия типа в понятное пользователю
    display_type = {
        "text": "Генерация текста",
        "image": "Генерация изображений"
    }.get(model_type, "Не выбран")

    return (
        "🤖 Главное меню\n\n"
        f"📊 Ваша статистика:\n"
        f"🎨 Сгенерировано изображений: {images_count}\n"
        f"📝 Сгенерировано текстов: {texts_count}\n\n"
        f"🔄 Текущая модель: {current_model}\n"
        f"📌 Тип: {display_type}\n\n"
        "Выберите действие:"
    )

async def safe_edit_message(message: types.Message, text: str, reply_markup=None):
    """Безопасное редактирование сообщения с обработкой ошибок."""
    try:
        # Проверяем, отличается ли новый текст или клавиатура от текущих
        current_text = message.text or message.caption
        if current_text == text:
            # Если текст не изменился, просто обновляем клавиатуру
            try:
                await message.edit_reply_markup(reply_markup=reply_markup)
            except TelegramBadRequest:
                pass
        else:
            # Если текст изменился, обновляем всё сообщение
            await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            # Если ошибка не связана с отсутствием изменений, отправляем новое сообщение
            await message.answer(text, reply_markup=reply_markup)
    except Exception as e:
        logging.error(f"Error editing message: {e}")
        await message.answer(text, reply_markup=reply_markup)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    get_user_stats(message.from_user.id)  # Инициализация статистики пользователя
    await message.answer(
        "👋 Привет! Я бот для работы с Pollinations.ai API.\n" + 
        get_menu_text(message.from_user.id),
        reply_markup=get_main_keyboard()
    )

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(HELP_TEXT, reply_markup=get_main_keyboard())

@dp.message(Command("about"))
async def cmd_about(message: types.Message):
    await message.answer(ABOUT_TEXT, reply_markup=get_main_keyboard())

@dp.message(Command("models"))
async def cmd_models(message: types.Message):
    await update_models(message)

@dp.callback_query(F.data == "help")
async def help_button(callback: types.CallbackQuery):
    await safe_edit_message(callback.message, HELP_TEXT, reply_markup=get_main_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "about")
async def about_button(callback: types.CallbackQuery):
    await safe_edit_message(callback.message, ABOUT_TEXT, reply_markup=get_main_keyboard())
    await callback.answer()

async def update_models(message: types.Message):
    """Обновление списка моделей через команду."""
    status_message = await message.answer("🔄 Загружаю список доступных моделей...")
    text_models, image_models = await fetch_all_models()
    
    if text_models and image_models:
        user_data[message.from_user.id] = {
            "text_models": text_models,
            "image_models": image_models
        }
        await status_message.edit_text(
            "✅ Списки моделей успешно обновлены!",
            reply_markup=get_main_keyboard()
        )
    else:
        await status_message.edit_text(
            "❌ Не удалось загрузить списки моделей",
            reply_markup=get_main_keyboard()
        )

@dp.callback_query(F.data == "update_models")
async def update_models_callback(callback: types.CallbackQuery):
    await callback.message.edit_text("🔄 Загружаю список доступных моделей...")
    text_models, image_models = await fetch_all_models()
    
    if text_models and image_models:
        user_data[callback.from_user.id] = {
            "text_models": text_models,
            "image_models": image_models
        }
        await safe_edit_message(
            callback.message,
            "✅ Списки моделей успешно обновлены!",
            reply_markup=get_main_keyboard()
        )
    else:
        await safe_edit_message(
            callback.message,
            "❌ Не удалось загрузить списки моделей",
            reply_markup=get_main_keyboard()
        )
    await callback.answer()

@dp.callback_query(F.data == "choose_model")
async def choose_model_type(callback: types.CallbackQuery):
    await safe_edit_message(
        callback.message,
        "Выберите тип моделей:",
        reply_markup=get_generation_type_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    await safe_edit_message(
        callback.message,
        get_menu_text(callback.from_user.id),
        reply_markup=get_main_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "select_image_models")
async def show_image_models(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    stats = get_user_stats(user_id)
    
    # Если моделей нет или они не загружены, загружаем их
    if not stats.get("image_models"):
        await safe_edit_message(
            callback.message,
            "🔄 Загружаю список моделей...",
            reply_markup=None
        )
        text_models, image_models = await fetch_all_models()
        if not image_models:
            await safe_edit_message(
                callback.message,
                "❌ Не удалось загрузить список моделей. Попробуйте позже.",
                reply_markup=get_main_keyboard()
            )
            await callback.answer()
            return
        
        stats["text_models"] = text_models
        stats["image_models"] = image_models
    
    await safe_edit_message(
        callback.message,
        "Выберите модель для генерации изображений:",
        reply_markup=get_models_keyboard(stats["image_models"], "image")
    )
    await callback.answer()

@dp.callback_query(F.data == "select_text_models")
async def show_text_models(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    stats = get_user_stats(user_id)
    
    # Если моделей нет или они не загружены, загружаем их
    if not stats.get("text_models"):
        await safe_edit_message(
            callback.message,
            "🔄 Загружаю список моделей...",
            reply_markup=None
        )
        text_models, image_models = await fetch_all_models()
        if not text_models:
            await safe_edit_message(
                callback.message,
                "❌ Не удалось загрузить список моделей. Попробуйте позже.",
                reply_markup=get_main_keyboard()
            )
            await callback.answer()
            return
        
        stats["text_models"] = text_models
        stats["image_models"] = image_models
    
    await safe_edit_message(
        callback.message,
        "Выберите модель для генерации текста:",
        reply_markup=get_models_keyboard(stats["text_models"], "text")
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("image_model_"))
async def image_model_selected(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    model_name = callback.data.replace("image_model_", "")
    stats = get_user_stats(user_id)
    stats["current_model"] = model_name
    stats["model_type"] = "image"
    
    await safe_edit_message(
        callback.message,
        f"✅ Выбрана модель для изображений: {model_name}\n\n" + 
        get_menu_text(user_id),
        reply_markup=get_main_keyboard()
    )
    await callback.answer("✅ Модель успешно выбрана!")

@dp.callback_query(F.data.startswith("text_model_"))
async def text_model_selected(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    model_name = callback.data.replace("text_model_", "")
    stats = get_user_stats(user_id)
    stats["current_model"] = model_name
    stats["model_type"] = "text"
    
    await safe_edit_message(
        callback.message,
        f"✅ Выбрана модель для текста: {model_name}\n\n" + 
        get_menu_text(user_id),
        reply_markup=get_main_keyboard()
    )
    await callback.answer("✅ Модель успешно выбрана!")

@dp.callback_query(F.data == "generate_image")
async def start_image_generation(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if user_id not in user_data or "current_model" not in user_data[user_id]:
        await safe_edit_message(
            callback.message,
            "❗ Сначала выберите модель через кнопку '🤖 Выбор модели'",
            reply_markup=get_main_keyboard()
        )
        await callback.answer()
        return
    
    if user_data[user_id].get("model_type") != "image":
        await safe_edit_message(
            callback.message,
            "❗ Выбранная модель не поддерживает генерацию изображений",
            reply_markup=get_main_keyboard()
        )
        await callback.answer()
        return
    
    await safe_edit_message(
        callback.message,
        "Введите описание изображения, которое хотите сгенерировать:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(UserState.waiting_for_image_prompt)
    await callback.answer()

@dp.callback_query(F.data == "generate_text")
async def start_text_generation(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if user_id not in user_data or "current_model" not in user_data[user_id]:
        await safe_edit_message(
            callback.message,
            "❗ Сначала выберите модель через кнопку '🤖 Выбор модели'",
            reply_markup=get_main_keyboard()
        )
        await callback.answer()
        return
    
    if user_data[user_id].get("model_type") != "text":
        await safe_edit_message(
            callback.message,
            "❗ Выбранная модель не поддерживает генерацию текста",
            reply_markup=get_main_keyboard()
        )
        await callback.answer()
        return
    
    await safe_edit_message(
        callback.message,
        "Введите текстовый запрос. Если хотите добавить изображение, просто отправьте его вместе с текстом:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(UserState.waiting_for_text_prompt)
    await callback.answer()

@dp.message(UserState.waiting_for_image_prompt)
async def process_image_prompt(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    stats = get_user_stats(user_id)
    model = stats["current_model"]
    
    status_message = await message.answer("🎨 Генерирую изображение, пожалуйста подождите...")
    
    image_url = await generate_image(model, message.text)
    if image_url:
        stats["images_generated"] += 1
        stats["last_used"] = datetime.now()
        await message.answer_photo(
            photo=image_url,
            caption=f"✨ Сгенерированное изображение\nПромпт: {message.text}"
        )
        await message.answer(get_menu_text(user_id), reply_markup=get_main_keyboard())
    else:
        await message.answer(
            "❌ Ошибка при генерации изображения",
            reply_markup=get_main_keyboard()
        )
    
    await status_message.delete()
    await state.clear()

@dp.message(UserState.waiting_for_text_prompt)
async def process_text_prompt(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    stats = get_user_stats(user_id)
    model = stats["current_model"]
    
    image_data = None
    if message.photo:
        photo = message.photo[-1]
        image_data = await bot.download(photo.file_id)
    
    status_message = await message.answer("📝 Генерирую текст, пожалуйста подождите...")
    
    response = await generate_text(model, message.text, image_data)
    if response:
        stats["texts_generated"] += 1
        stats["last_used"] = datetime.now()
        await message.answer(response)
        await message.answer(get_menu_text(user_id), reply_markup=get_main_keyboard())
    else:
        await message.answer(
            "❌ Произошла ошибка при генерации текста. Попробуйте еще раз.",
            reply_markup=get_main_keyboard()
        )
    
    await status_message.delete()
    await state.clear()

@dp.callback_query(F.data == "cancel")
async def cancel_action(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_edit_message(
        callback.message,
        "❌ Действие отменено\nВыберите действие:",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 