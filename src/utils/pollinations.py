import aiohttp
import base64
import mimetypes
from urllib.parse import quote_plus
from config.config import TEXT_MODELS_URL, IMAGE_MODELS_URL, TEXT_GENERATION_OPENAI_URL, IMAGE_GENERATION_BASE_URL
import logging
from src.managers.chat_manager import chat_manager

async def fetch_models(url: str) -> list:
    """Асинхронно получает список моделей с указанного URL."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return None
    except Exception as e:
        print(f"Ошибка при запросе моделей: {e}")
        return None

async def fetch_all_models():
    """Получает списки всех доступных моделей."""
    text_models = await fetch_models(TEXT_MODELS_URL)
    image_models = await fetch_models(IMAGE_MODELS_URL)
    return text_models, image_models

async def encode_image_to_base64(image_bytes: bytes) -> tuple:
    """Кодирует изображение в base64 строку и определяет MIME-тип."""
    try:
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        # Определяем MIME-тип по первым байтам
        mime_type = "image/jpeg"  # По умолчанию
        if image_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
            mime_type = "image/png"
        elif image_bytes.startswith(b'\xff\xd8'):
            mime_type = "image/jpeg"
        return base64_image, mime_type
    except Exception as e:
        print(f"Ошибка при кодировании изображения: {e}")
        return None, None

async def generate_text(model_name: str, prompt: str, image_data: bytes = None, user_id: int = None) -> str:
    """Генерирует текст с использованием выбранной модели."""
    try:
        messages = []
        
        # Получаем историю чата, если указан user_id
        if user_id:
            chat_history = await chat_manager.get_context(user_id)
            messages.extend(chat_history)
        
        if image_data:
            image_base64, mime_type = await encode_image_to_base64(image_data)
            if image_base64 and mime_type:
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{image_base64}"}
                        }
                    ]
                })
            else:
                # Если не удалось закодировать изображение, продолжаем только с текстом
                messages.append({"role": "user", "content": prompt})
        else:
            messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model_name,
            "messages": messages
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(TEXT_GENERATION_OPENAI_URL, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("choices") and len(result["choices"]) > 0:
                        content = result["choices"][0].get("message", {}).get("content")
                        if content:
                            # Сохраняем ответ модели в историю чата
                            if user_id:
                                await chat_manager.add_message(user_id, prompt, role="user")
                                await chat_manager.add_message(user_id, content, role="assistant")
                            return content
                        return "Модель вернула пустой ответ"
                return f"Ошибка при генерации текста. Статус: {response.status}"
    except Exception as e:
        logging.error(f"Ошибка при генерации текста: {str(e)}")
        return f"Произошла ошибка при обработке запроса: {str(e)}"

async def generate_image(model_name: str, prompt: str) -> str:
    """Генерирует изображение с использованием выбранной модели."""
    try:
        encoded_prompt = quote_plus(prompt)
        request_url = f"{IMAGE_GENERATION_BASE_URL}{encoded_prompt}?model={model_name}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(request_url) as response:
                if response.status == 200:
                    return request_url
                return None
    except Exception as e:
        print(f"Ошибка при генерации изображения: {e}")
        return None 