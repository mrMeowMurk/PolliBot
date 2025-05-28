from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.managers.chat_manager import chat_manager
from src.keyboards.keyboards import get_main_keyboard, get_chat_history_keyboard

router = Router()

@router.message(Command("history"))
@router.callback_query(lambda c: c.data == "show_history")
async def show_chat_history(event: Message | CallbackQuery):
    """Показать историю чата пользователя."""
    # Получаем user_id в зависимости от типа события
    if isinstance(event, Message):
        user_id = event.from_user.id
        message = event
    else:
        user_id = event.from_user.id
        message = event.message
    
    history = await chat_manager.get_recent_history(user_id)
    
    if not history:
        response = "История чата пуста."
        if isinstance(event, CallbackQuery):
            await message.edit_text(response, reply_markup=get_main_keyboard())
            await event.answer()
        else:
            await message.answer(response, reply_markup=get_main_keyboard())
        return
    
    response = "📜 Последние сообщения в чате:\n\n"
    for msg in history:
        role = "👤 Вы" if msg["role"] == "user" else "🤖 Бот"
        response += f"{role}: {msg['message']}\n"
    
    if isinstance(event, CallbackQuery):
        await message.edit_text(response, reply_markup=get_chat_history_keyboard())
        await event.answer()
    else:
        await message.answer(response, reply_markup=get_chat_history_keyboard())

@router.callback_query(lambda c: c.data == "clear_history")
async def clear_history(callback: CallbackQuery):
    """Очистить историю чата."""
    user_id = callback.from_user.id
    await chat_manager.clear_user_history(user_id)
    await callback.message.edit_text("История чата очищена.", reply_markup=get_main_keyboard())
    await callback.answer() 