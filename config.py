from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# API URLs
TEXT_MODELS_URL = "https://text.pollinations.ai/models"
IMAGE_MODELS_URL = "https://image.pollinations.ai/models"
TEXT_GENERATION_OPENAI_URL = "https://text.pollinations.ai/openai"
IMAGE_GENERATION_BASE_URL = "https://image.pollinations.ai/prompt/"

# Доступные модели
AVAILABLE_MODELS = {
    "Stable Diffusion XL": "sd_xl",
    "Stable Diffusion 1.5": "sd_1_5",
    "Kandinsky": "kandinsky",
    "DALL-E": "dalle"
}

# Текст для команд
HELP_TEXT = """
🤖 Доступные команды:
/start - Начать работу с ботом
/help - Показать это сообщение
/about - Информация о боте
/models - Обновить список доступных моделей

Используйте кнопки меню для:
- Генерации изображений
- Генерации текста
- Выбора модели
"""

ABOUT_TEXT = """
🎨 Многофункциональный бот для работы с Pollinations.ai API

Поддерживаемые функции:
- Генерация изображений по текстовому описанию
- Генерация текста с поддержкой изображений
- Выбор различных моделей для генерации
- Удобное меню управления

API: Pollinations.ai
Фреймворк: aiogram 3.x
""" 