from datetime import datetime
from aiogram import types, Bot
from aiogram.fsm.context import FSMContext

from src.keyboards.keyboards import get_main_keyboard, get_cancel_keyboard
from src.utils.message import safe_edit_message
from src.utils.user_data import get_user_stats, get_menu_text, update_user_stats
from src.utils.pollinations import generate_text, generate_image
from src.states.user import UserState

async def start_image_generation(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    stats = get_user_stats(user_id)
    
    if not stats.get("current_model"):
        await safe_edit_message(
            callback.message,
            "❗ Сначала выберите модель через кнопку '🤖 Выбор модели'",
            reply_markup=get_main_keyboard()
        )
        await callback.answer()
        return
    
    if stats.get("model_type") != "image":
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

async def start_text_generation(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    stats = get_user_stats(user_id)
    
    if not stats.get("current_model"):
        await safe_edit_message(
            callback.message,
            "❗ Сначала выберите модель через кнопку '🤖 Выбор модели'",
            reply_markup=get_main_keyboard()
        )
        await callback.answer()
        return
    
    if stats.get("model_type") != "text":
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

async def process_image_prompt(message: types.Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    stats = get_user_stats(user_id)
    model = stats["current_model"]
    
    status_message = await message.answer("🎨 Генерирую изображение, пожалуйста подождите...")
    
    image_url = await generate_image(model, message.text)
    if image_url:
        stats["images_generated"] += 1
        stats["last_used"] = datetime.now()
        update_user_stats(user_id, stats)
        
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

async def process_text_prompt(message: types.Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    stats = get_user_stats(user_id)
    model = stats["current_model"]

    # Проверяем наличие изображения и получаем текст
    image_data_bytes = None
    prompt_text = message.text

    if message.photo:
        photo = message.photo[-1]  # Берем самое большое изображение
        image_data_io = await bot.download(photo.file_id)
        # Читаем байты из BytesIO объекта
        image_data_bytes = image_data_io.read()
        # При наличии фото, текст находится в подписи (caption)
        prompt_text = message.caption

    # Проверяем наличие текста или подписи
    if not prompt_text:
        await message.answer(
            "❗ Пожалуйста, введите текстовый запрос или добавьте подпись к изображению",
            reply_markup=get_cancel_keyboard()
        )
        return

    status_message = await message.answer(
        "📝 Генерирую ответ, пожалуйста подождите..." +
        ("\n🖼 Анализирую изображение..." if image_data_bytes else "")
    )

    # Передаем изображение в байтах и текст в функцию генерации
    response = await generate_text(model, prompt_text, image_data_bytes, user_id)
    if response:
        stats["texts_generated"] += 1
        stats["last_used"] = datetime.now()
        update_user_stats(user_id, stats)

        # Отправляем ответ с форматированием
        await message.answer(
            f"✨ Ответ модели:\n\n{response}",
            parse_mode="HTML"
        )
        await message.answer(get_menu_text(user_id), reply_markup=get_main_keyboard())
    else:
        await message.answer(
            "❌ Произошла ошибка при генерации текста. Попробуйте еще раз.",
            reply_markup=get_main_keyboard()
        )

    await status_message.delete()
    await state.clear()

async def cancel_action(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_edit_message(
        callback.message,
        "❌ Действие отменено\n" + get_menu_text(callback.from_user.id),
        reply_markup=get_main_keyboard()
    )
    await callback.answer()
