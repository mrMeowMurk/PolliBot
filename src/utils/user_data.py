from typing import Dict, Any
from src.managers.database import db

# Хранилище данных пользователей
user_data = {}

def get_user_stats(user_id: int) -> dict:
    """Получение статистики пользователя."""
    return db.get_user_stats(user_id)

def update_user_stats(user_id: int, stats: Dict[str, Any]) -> None:
    """Обновление статистики пользователя."""
    db.update_user_stats(user_id, stats)

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