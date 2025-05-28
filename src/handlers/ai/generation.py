from datetime import datetime
from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from io import BytesIO
from aiogram.types import BufferedInputFile

from src.keyboards.keyboards import get_main_keyboard, get_cancel_keyboard, get_generation_response_keyboard, get_audio_generation_options_keyboard, get_voice_selection_keyboard
from src.utils.message import safe_edit_message
from src.utils.user_data import get_user_stats, get_menu_text, update_user_stats
from src.utils.pollinations import generate_text, generate_image, generate_audio
from src.states.user import UserState
from config.config import AVAILABLE_VOICES

async def start_image_generation(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    stats = get_user_stats(user_id)
    
    if not stats.get("current_model"):
        await safe_edit_message(
            callback.message,
            "❗ Сначала выберите модель через кнопку '🤖 Выбор модели' -> '🎨 Изображения'",
            reply_markup=get_main_keyboard()
        )
        await callback.answer()
        return
    
    if stats.get("model_type") != "image":
        await safe_edit_message(
            callback.message,
            "❗ Выбранная модель не поддерживает генерацию изображений. Выберите модель для изображений через '🤖 Выбор модели' -> '🎨 Изображения'",
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
            "❗ Сначала выберите модель через кнопку '🤖 Выбор модели' -> '📝 Текст'",
            reply_markup=get_main_keyboard()
        )
        await callback.answer()
        return
    
    if stats.get("model_type") != "text":
        await safe_edit_message(
            callback.message,
            "❗ Выбранная модель не поддерживает генерацию текста. Выберите модель для текста через '🤖 Выбор модели' -> '📝 Текст'",
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

async def start_audio_generation(callback: types.CallbackQuery, state: FSMContext):
    await safe_edit_message(
        callback.message,
        "Выберите тип генерации аудио:",
        reply_markup=get_audio_generation_options_keyboard()
    )
    await state.set_state(UserState.waiting_for_audio_generation_type)
    await callback.answer()

async def start_echo_audio_generation(callback: types.CallbackQuery, state: FSMContext):
    await safe_edit_message(
        callback.message,
        "Введите текст для озвучивания:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(UserState.waiting_for_audio_prompt)
    # Сохраняем тип аудио генерации в состоянии
    await state.update_data(audio_gen_type="echo")
    await callback.answer()

async def start_response_audio_generation(callback: types.CallbackQuery, state: FSMContext):
    await safe_edit_message(
        callback.message,
        "Введите текстовый запрос для аудио ответа:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(UserState.waiting_for_audio_prompt)
    # Сохраняем тип аудио генерации в состоянии
    await state.update_data(audio_gen_type="response")
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

    # Сохраняем последний запрос пользователя и данные изображения в состояние FSM
    await state.update_data(last_prompt_text=prompt_text, last_image_data=image_data_bytes)

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
        await status_message.edit_text(
            f"✨ Ответ от модели <b>{model}</b>:\n\n{response}",
            parse_mode="HTML",
            reply_markup=get_generation_response_keyboard()
        )
        # Не сбрасываем состояние, остаемся в ожидании текста

    else:
        await status_message.edit_text(
            "❌ Произошла ошибка при генерации текста. Попробуйте еще раз.",
            reply_markup=get_main_keyboard()
        )
        await state.clear() # Сбрасываем состояние при ошибке

async def process_audio_prompt(message: types.Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    stats = get_user_stats(user_id)
    prompt_text = message.text

    if not prompt_text:
        await message.answer(
            "❗ Пожалуйста, введите текст для озвучивания",
            reply_markup=get_cancel_keyboard()
        )
        return

    data = await state.get_data()
    audio_gen_type = data.get("audio_gen_type")
    
    # Получаем выбранный голос из статистики пользователя
    selected_voice = stats.get("current_voice", "alloy")
    if selected_voice in AVAILABLE_VOICES:
        voice_id = AVAILABLE_VOICES[selected_voice]
    else:
        voice_id = "alloy"  # Используем голос по умолчанию, если выбранный голос не найден

    # Сохраняем последний аудио запрос и тип генерации в состоянии
    await state.update_data(
        last_audio_prompt=prompt_text,
        audio_gen_type=audio_gen_type
    )

    status_message = await message.answer("🎵 Генерирую аудио, пожалуйста подождите...")
    
    if audio_gen_type == "response":
        # Для типа "response" сначала генерируем текстовый ответ
        if not stats.get("current_model"):
            await status_message.edit_text(
                "❗ Сначала выберите текстовую модель через кнопку '🤖 Выбор модели' -> '📝 Текст'",
                reply_markup=get_main_keyboard()
            )
            await state.clear()
            return

        if stats.get("model_type") != "text":
            await status_message.edit_text(
                "❗ Выбранная модель не поддерживает генерацию текста. Выберите модель для текста через '🤖 Выбор модели' -> '📝 Текст'",
                reply_markup=get_main_keyboard()
            )
            await state.clear()
            return

        # Генерируем текстовый ответ
        response = await generate_text(stats["current_model"], prompt_text, None, user_id)
        if not response:
            await status_message.edit_text(
                "❌ Произошла ошибка при генерации текста. Попробуйте еще раз.",
                reply_markup=get_main_keyboard()
            )
            await state.clear()
            return

        # Используем сгенерированный текст для озвучивания
        text_to_speak = response
        caption = f"🎵 Сгенерированное аудио\n\nТип генерации: {audio_gen_type}\nГолос: {selected_voice}\n\nТекстовый ответ:\n{response}"
    else:
        # Для типа "echo" просто озвучиваем введенный текст
        text_to_speak = prompt_text
        caption = f"🎵 Сгенерированное аудио\n\nТип генерации: {audio_gen_type}\nГолос: {selected_voice}"

    # Генерируем аудио
    audio_data = await generate_audio("openai-audio", text_to_speak, voice=voice_id)

    if audio_data:
        stats["audio_generated"] = stats.get("audio_generated", 0) + 1
        stats["last_used"] = datetime.now()
        update_user_stats(user_id, stats)

        audio_io = BytesIO(audio_data)
        audio_io.name = "generated_audio.mp3"

        await status_message.edit_text("✅ Аудио сгенерировано!")
        # Отправляем аудио без кнопок
        await message.answer_audio(
            audio=BufferedInputFile(audio_io.read(), filename=audio_io.name),
            caption=caption
        )
        # Отправляем меню отдельным сообщением
        await message.answer(
            get_menu_text(user_id),
            reply_markup=get_main_keyboard()
        )
    else:
        await status_message.edit_text(
            "❌ Произошла ошибка при генерации аудио. Попробуйте еще раз.",
            reply_markup=get_main_keyboard()
        )
        await state.clear()

async def cancel_action(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await safe_edit_message(
        callback.message,
        "❌ Действие отменено\n" + get_menu_text(callback.from_user.id),
        reply_markup=get_main_keyboard()
    )
    await callback.answer()

async def back_to_menu_from_generation(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    # Отправляем новое сообщение с меню вместо редактирования
    await callback.message.answer(
        get_menu_text(callback.from_user.id),
        reply_markup=get_main_keyboard()
    )
    await callback.answer()

async def redo_text_generation(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    user_id = callback.from_user.id
    stats = get_user_stats(user_id)
    model = stats["current_model"]

    data = await state.get_data()
    last_prompt_text = data.get("last_prompt_text")
    last_image_data_bytes = data.get("last_image_data")

    if not last_prompt_text and not last_image_data_bytes:
        await callback.message.answer(
            "Нет предыдущего запроса для повторной генерации.",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
        await callback.answer()
        return

    # Отправляем новое сообщение о статусе вместо редактирования
    status_message = await callback.message.answer(
        "🔄 Переделываю ответ..." +
        ("\n🖼 Анализирую изображение..." if last_image_data_bytes else "")
    )

    # Передаем сохраненные данные изображения и текст в функцию генерации
    response = await generate_text(model, last_prompt_text, last_image_data_bytes, user_id)

    if response:
        stats["texts_generated"] += 1 # Учитываем повторную генерацию в статистике
        stats["last_used"] = datetime.now()
        update_user_stats(user_id, stats)

        # Отправляем новое сообщение с ответом вместо редактирования
        await callback.message.answer(
            f"✨ Ответ от модели <b>{model}</b>:\n\n{response}",
            parse_mode="HTML",
            reply_markup=get_generation_response_keyboard()
        )
        # Остаемся в состоянии ожидания текста

    else:
        # Отправляем новое сообщение об ошибке вместо редактирования
        await callback.message.answer(
            "❌ Произошла ошибка при повторной генерации текста. Попробуйте еще раз.",
            reply_markup=get_main_keyboard()
        )
        await state.clear() # Сбрасываем состояние при ошибке

    await callback.answer()

async def choose_voice(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик для выбора голоса."""
    await callback.answer()
    await callback.message.edit_text(
        "Выберите голос для генерации аудио:",
        reply_markup=get_voice_selection_keyboard()
    )

async def voice_selected(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик для выбора конкретного голоса."""
    await callback.answer()
    voice_name = callback.data.split(":")[1]
    voice_id = AVAILABLE_VOICES.get(voice_name)
    
    if voice_id:
        # Сохраняем выбранный голос в состоянии
        await state.update_data(selected_voice=voice_id)
        # Обновляем статистику пользователя
        user_id = callback.from_user.id
        stats = get_user_stats(user_id)
        stats["current_voice"] = voice_name
        update_user_stats(user_id, stats)
        
        await callback.message.edit_text(
            get_menu_text(user_id),
            reply_markup=get_main_keyboard()
        )
    else:
        await callback.message.edit_text(
            "Произошла ошибка при выборе голоса. Попробуйте еще раз.",
            reply_markup=get_voice_selection_keyboard()
        )

async def redo_audio_generation(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Обработчик для повторной генерации аудио."""
    data = await state.get_data()
    last_prompt = data.get("last_audio_prompt")
    
    if not last_prompt:
        await callback.message.answer(
            "Нет предыдущего запроса для повторной генерации.",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
        await callback.answer()
        return

    user_id = callback.from_user.id
    stats = get_user_stats(user_id)
    
    # Получаем выбранный голос из статистики пользователя
    selected_voice = stats.get("current_voice", "alloy")
    if selected_voice in AVAILABLE_VOICES:
        voice_id = AVAILABLE_VOICES[selected_voice]
    else:
        voice_id = "alloy"  # Используем голос по умолчанию, если выбранный голос не найден

    # Отправляем новое сообщение о статусе вместо редактирования
    status_message = await callback.message.answer("🔄 Переделываю аудио...")

    # Генерируем аудио напрямую
    audio_data = await generate_audio("openai-audio", last_prompt, voice=voice_id)

    if audio_data:
        stats["audio_generated"] = stats.get("audio_generated", 0) + 1
        stats["last_used"] = datetime.now()
        update_user_stats(user_id, stats)

        audio_io = BytesIO(audio_data)
        audio_io.name = "generated_audio.mp3"

        # Отправляем новое сообщение о статусе вместо редактирования
        await callback.message.answer("✅ Аудио перегенерировано!")
        # Отправляем аудио без кнопок
        await callback.message.answer_audio(
            audio=BufferedInputFile(audio_io.read(), filename=audio_io.name),
            caption=f"🎵 Сгенерированное аудио\n\nТип генерации: {data.get('audio_gen_type')}\nГолос: {selected_voice}"
        )
        # Отправляем меню отдельным сообщением
        await callback.message.answer(
            get_menu_text(user_id),
            reply_markup=get_main_keyboard()
        )
    else:
        # Отправляем новое сообщение об ошибке вместо редактирования
        await callback.message.answer(
            "❌ Произошла ошибка при повторной генерации аудио. Попробуйте еще раз.",
            reply_markup=get_main_keyboard()
        )
        await state.clear()

    await callback.answer()
