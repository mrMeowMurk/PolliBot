import logging
from aiogram import types
from aiogram.exceptions import TelegramBadRequest

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