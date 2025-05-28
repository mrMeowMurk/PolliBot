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
    """Получает текст для главного меню с информацией о пользователе."""
    stats = get_user_stats(user_id)
    
    # Получаем информацию о текущей модели
    current_model = stats.get("current_model", "Не выбрана")
    model_type = stats.get("model_type", "Не выбран")
    
    # Получаем информацию о текущем голосе
    current_voice = stats.get("current_voice", "Не выбран")
    
    # Форматируем текст меню
    menu_text = f"""
<b>🤖 Главное меню</b>

<b>📊 Статистика:</b>
• Сгенерировано изображений: {stats.get('images_generated', 0)}
• Сгенерировано текстов: {stats.get('texts_generated', 0)}
• Сгенерировано аудио: {stats.get('audio_generated', 0)}

<b>⚙️ Текущие настройки:</b>
• Модель: {current_model}
• Тип модели: {model_type}
• Голос: {current_voice}

<b>🕒 Последнее использование:</b>
• {stats.get('last_used', 'Никогда')}
"""
    return menu_text 