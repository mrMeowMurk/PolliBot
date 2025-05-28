from aiogram import types
from aiogram.fsm.context import FSMContext

from src.keyboards.keyboards import get_main_keyboard, get_models_keyboard, get_generation_type_keyboard
from src.utils.message import safe_edit_message
from src.utils.user_data import get_user_stats, get_menu_text, update_user_stats
from src.utils.pollinations import fetch_all_models

async def choose_model_type(callback: types.CallbackQuery):
    await safe_edit_message(
        callback.message,
        "Выберите тип моделей:",
        reply_markup=get_generation_type_keyboard()
    )
    await callback.answer()

async def show_text_models(callback: types.CallbackQuery):
    await callback.answer("🔄 Загрузка моделей...")
    user_id = callback.from_user.id
    stats = get_user_stats(user_id)
    
    if not stats.get("text_models"):
        await safe_edit_message(
            callback.message,
            "🔄 Загружаю список моделей...",
            reply_markup=None
        )
        text_models, image_models, audio_models = await fetch_all_models()
        if not text_models:
            await safe_edit_message(
                callback.message,
                "❌ Не удалось загрузить список моделей. Попробуйте позже.",
                reply_markup=get_main_keyboard()
            )
            return
        
        stats["text_models"] = text_models
        stats["image_models"] = image_models
        stats["audio_models"] = audio_models
        update_user_stats(user_id, stats)
    
    await safe_edit_message(
        callback.message,
        "Выберите модель для генерации текста:",
        reply_markup=get_models_keyboard(stats["text_models"], "text")
    )

async def show_image_models(callback: types.CallbackQuery):
    await callback.answer("🔄 Загрузка моделей...")
    user_id = callback.from_user.id
    stats = get_user_stats(user_id)
    
    if not stats.get("image_models"):
        await safe_edit_message(
            callback.message,
            "🔄 Загружаю список моделей...",
            reply_markup=None
        )
        text_models, image_models, audio_models = await fetch_all_models()
        if not image_models:
            await safe_edit_message(
                callback.message,
                "❌ Не удалось загрузить список моделей. Попробуйте позже.",
                reply_markup=get_main_keyboard()
            )
            return
        
        stats["text_models"] = text_models
        stats["image_models"] = image_models
        stats["audio_models"] = audio_models
        update_user_stats(user_id, stats)
    
    await safe_edit_message(
        callback.message,
        "Выберите модель для генерации изображений:",
        reply_markup=get_models_keyboard(stats["image_models"], "image")
    )

async def show_audio_models(callback: types.CallbackQuery):
    await callback.answer("🔄 Загрузка моделей...")
    user_id = callback.from_user.id
    stats = get_user_stats(user_id)
    
    if not stats.get("audio_models"):
        await safe_edit_message(
            callback.message,
            "🔄 Загружаю список моделей...",
            reply_markup=None
        )
        text_models, image_models, audio_models = await fetch_all_models()
        if not audio_models:
            await safe_edit_message(
                callback.message,
                "❌ Не удалось загрузить список моделей. Попробуйте позже.",
                reply_markup=get_main_keyboard()
            )
            return
        
        stats["text_models"] = text_models
        stats["image_models"] = image_models
        stats["audio_models"] = audio_models
        update_user_stats(user_id, stats)
    
    await safe_edit_message(
        callback.message,
        "Выберите модель для генерации аудио:",
        reply_markup=get_models_keyboard(stats["audio_models"], "audio")
    )

async def text_model_selected(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    model_name = callback.data.replace("text_model_", "")
    stats = get_user_stats(user_id)
    
    # Сохраняем выбранную модель и её тип
    stats["current_model"] = model_name
    stats["model_type"] = "text"
    update_user_stats(user_id, stats)
    
    await safe_edit_message(
        callback.message,
        get_menu_text(user_id),
        reply_markup=get_main_keyboard()
    )
    await callback.answer("✅ Модель успешно выбрана!")

async def image_model_selected(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    model_name = callback.data.replace("image_model_", "")
    stats = get_user_stats(user_id)
    
    # Сохраняем выбранную модель и её тип
    stats["current_model"] = model_name
    stats["model_type"] = "image"
    update_user_stats(user_id, stats)
    
    await safe_edit_message(
        callback.message,
        get_menu_text(user_id),
        reply_markup=get_main_keyboard()
    )
    await callback.answer("✅ Модель успешно выбрана!")

async def audio_model_selected(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    model_name = callback.data.replace("audio_model_", "")
    stats = get_user_stats(user_id)
    
    # Сохраняем выбранную модель и её тип
    stats["current_model"] = model_name
    stats["model_type"] = "audio"
    update_user_stats(user_id, stats)
    
    await safe_edit_message(
        callback.message,
        get_menu_text(user_id),
        reply_markup=get_main_keyboard()
    )
    await callback.answer("✅ Модель успешно выбрана!")

async def update_models_callback(callback: types.CallbackQuery):
    await callback.message.edit_text("🔄 Загружаю список доступных моделей...")
    text_models, image_models, audio_models = await fetch_all_models()
    
    if text_models and image_models and audio_models:
        stats = get_user_stats(callback.from_user.id)
        stats["text_models"] = text_models
        stats["image_models"] = image_models
        stats["audio_models"] = audio_models
        update_user_stats(callback.from_user.id, stats)
        
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