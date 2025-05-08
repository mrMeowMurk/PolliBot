from aiogram import types
from aiogram.filters.command import Command

from config.config import HELP_TEXT, ABOUT_TEXT
from src.keyboards.keyboards import get_main_keyboard
from src.utils.user_data import get_user_stats, get_menu_text
from src.utils.message import safe_edit_message

async def cmd_start(message: types.Message):
    get_user_stats(message.from_user.id)  # Инициализация статистики пользователя
    await message.answer(
        "👋 Привет! Я бот для работы с Pollinations.ai API.\n" + 
        get_menu_text(message.from_user.id),
        reply_markup=get_main_keyboard()
    )

async def cmd_help(message: types.Message):
    await message.answer(HELP_TEXT, reply_markup=get_main_keyboard())

async def cmd_about(message: types.Message):
    await message.answer(ABOUT_TEXT, reply_markup=get_main_keyboard())

async def help_button(callback: types.CallbackQuery):
    await safe_edit_message(callback.message, HELP_TEXT, reply_markup=get_main_keyboard())
    await callback.answer()

async def about_button(callback: types.CallbackQuery):
    await safe_edit_message(callback.message, ABOUT_TEXT, reply_markup=get_main_keyboard())
    await callback.answer()

async def back_to_menu(callback: types.CallbackQuery):
    await safe_edit_message(
        callback.message,
        get_menu_text(callback.from_user.id),
        reply_markup=get_main_keyboard()
    )
    await callback.answer()