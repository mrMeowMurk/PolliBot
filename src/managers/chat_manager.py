from typing import List, Dict, Any
from datetime import datetime
from .database import db

class ChatManager:
    def __init__(self):
        self.db = db

    async def add_message(self, user_id: int, message: str, role: str = "user") -> None:
        """Добавление сообщения в историю чата."""
        self.db.add_chat_message(user_id, message, role)

    async def get_context(self, user_id: int, max_tokens: int = 2000) -> List[Dict[str, str]]:
        """Получение контекста чата с учетом ограничения токенов."""
        return self.db.get_chat_context(user_id, max_tokens)

    async def clear_old_messages(self, days: int = 7) -> None:
        """Очистка старых сообщений для всех пользователей."""
        self.db.clear_old_messages(days)

    async def clear_user_history(self, user_id: int) -> None:
        """Очистка всей истории чата для конкретного пользователя."""
        self.db.clear_user_history(user_id)

    async def get_recent_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Получение последних сообщений из истории."""
        return self.db.get_chat_history(user_id, limit)

# Создаем глобальный экземпляр менеджера чата
chat_manager = ChatManager() 