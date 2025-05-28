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
    "DALL-E": "dalle",
    "OpenAI Audio": "openai-audio"
}

# Доступные голоса для генерации аудио
AVAILABLE_VOICES = {
    "Alloy": "alloy",
    "Echo": "echo",
    "Fable": "fable",
    "Onyx": "onyx",
    "Nova": "nova",
    "Shimmer": "shimmer"
}

# Текст для команд
HELP_TEXT = """
<b>🤖 Доступные команды:</b>

Используйте кнопки меню для:

- 🖼️ <b>Генерация изображений по описанию</b>
- 📝 <b>Генерация текста</b> (с поддержкой изображений в запросах) 
- 🎵 <b>Генерации аудио</b> 
  - Генерация аудио ответа
  - Озвучивание текста (echo)
- 🤖 <b>Выбора модели для генерации</b> 
- 🔄 <b>Обновления доступных моделей</b> 
- 📜 <b>Просмотра истории чата</b> 

После получения ответа от модели текста, вы можете <b>🔄 переделать его</b> или <b>⬅️ вернуться в меню</b>.
"""

ABOUT_TEXT = """
<b>🎨 Многофункциональный бот для работы с <code>Pollinations.ai</code> API</b>

<b>✨ Поддерживаемые функции:</b>

- 🖼️ <b>Генерация изображений по текстовому описанию</b>
- 📝 <b>Генерация текста с поддержкой изображений в запросах</b>
- 🎵 <b>Генерация аудио из текста</b> (с выбором режима: ответ или echo)
- 🤖 <b>Выбор различных моделей для генерации</b>
- 💾 <b>Удобное управление</b> через inline-кнопки
- 📊 <b>Статистика использования</b> для каждого пользователя
- 💾 <b>Сохранение истории чата</b>

API: <code>Pollinations.ai</code>
Фреймворк: <code>aiogram 3.x</code>
""" 