import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple

class DatabaseManager:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_file: str = "bot.db"):
        # Инициализируем только один раз
        if not DatabaseManager._initialized:
            # Создаем директорию data, если она не существует
            os.makedirs(os.path.dirname(db_file), exist_ok=True)
            self.db_file = db_file
            self._create_tables()
            DatabaseManager._initialized = True

    def _create_tables(self) -> None:
        """Создание необходимых таблиц в базе данных."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            # Таблица пользователей
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    images_generated INTEGER DEFAULT 0,
                    texts_generated INTEGER DEFAULT 0,
                    audio_generated INTEGER DEFAULT 0,
                    last_used TIMESTAMP,
                    current_model TEXT,
                    model_type TEXT,
                    current_voice TEXT
                )
            """)
            
            # Таблица для хранения моделей пользователей
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_models (
                    user_id INTEGER,
                    model_type TEXT,
                    models TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    PRIMARY KEY (user_id, model_type)
                )
            """)

            # Таблица для хранения истории чата
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message TEXT,
                    role TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            conn.commit()

    def add_chat_message(self, user_id: int, message: str, role: str = "user") -> None:
        """Добавление сообщения в историю чата."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_history (user_id, message, role)
                VALUES (?, ?, ?)
            """, (user_id, message, role))
            conn.commit()

    def get_chat_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Получение истории чата пользователя."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT message, role, timestamp
                FROM chat_history
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, limit))
            
            return [
                {
                    "message": row[0],
                    "role": row[1],
                    "timestamp": row[2]
                }
                for row in cursor.fetchall()
            ]

    def clear_old_messages(self, days: int = 7) -> None:
        """Очистка старых сообщений из истории чата."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cutoff_date = datetime.now() - timedelta(days=days)
            cursor.execute("""
                DELETE FROM chat_history
                WHERE timestamp < ?
            """, (cutoff_date,))
            conn.commit()

    def clear_user_history(self, user_id: int) -> None:
        """Очистка всей истории чата для конкретного пользователя."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM chat_history
                WHERE user_id = ?
            """, (user_id,))
            conn.commit()

    def get_chat_context(self, user_id: int, max_tokens: int = 2000) -> List[Dict[str, str]]:
        """Получение контекста чата с учетом ограничения токенов."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT message, role
                FROM chat_history
                WHERE user_id = ?
                ORDER BY timestamp DESC
            """, (user_id,))
            
            messages = []
            total_tokens = 0
            
            for row in cursor.fetchall():
                message = row[0]
                role = row[1]
                # Примерная оценка токенов (4 символа ~ 1 токен)
                message_tokens = len(message) // 4
                
                if total_tokens + message_tokens > max_tokens:
                    break
                    
                messages.insert(0, {"role": role, "content": message})
                total_tokens += message_tokens
            
            return messages

    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Получение статистики пользователя."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            # Проверяем существование пользователя
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                # Создаем нового пользователя
                cursor.execute(
                    "INSERT INTO users (user_id, images_generated, texts_generated, audio_generated) VALUES (?, 0, 0, 0)",
                    (user_id,)
                )
                conn.commit()
                return {
                    "images_generated": 0,
                    "texts_generated": 0,
                    "audio_generated": 0,
                    "last_used": None,
                    "current_model": None,
                    "model_type": None,
                    "current_voice": None,
                    "text_models": None,
                    "image_models": None,
                    "audio_models": None
                }
            
            # Получаем модели пользователя
            cursor.execute(
                "SELECT model_type, models FROM user_models WHERE user_id = ?",
                (user_id,)
            )
            models = {row[0]: eval(row[1]) for row in cursor.fetchall()}
            
            return {
                "images_generated": user[1],
                "texts_generated": user[2],
                "audio_generated": user[3],
                "last_used": user[4],
                "current_model": user[5],
                "model_type": user[6],
                "current_voice": user[7],
                "text_models": models.get("text"),
                "image_models": models.get("image"),
                "audio_models": models.get("audio")
            }

    def update_user_stats(self, user_id: int, stats: Dict[str, Any]) -> None:
        """Обновление статистики пользователя."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            # Обновляем основные данные пользователя
            cursor.execute("""
                UPDATE users 
                SET images_generated = ?,
                    texts_generated = ?,
                    audio_generated = ?,
                    last_used = ?,
                    current_model = ?,
                    model_type = ?,
                    current_voice = ?
                WHERE user_id = ?
            """, (
                stats.get("images_generated", 0),
                stats.get("texts_generated", 0),
                stats.get("audio_generated", 0),
                stats.get("last_used"),
                stats.get("current_model"),
                stats.get("model_type"),
                stats.get("current_voice"),
                user_id
            ))
            
            # Обновляем модели пользователя
            if "text_models" in stats:
                cursor.execute("""
                    INSERT OR REPLACE INTO user_models (user_id, model_type, models)
                    VALUES (?, 'text', ?)
                """, (user_id, str(stats["text_models"])))
            
            if "image_models" in stats:
                cursor.execute("""
                    INSERT OR REPLACE INTO user_models (user_id, model_type, models)
                    VALUES (?, 'image', ?)
                """, (user_id, str(stats["image_models"])))
            
            if "audio_models" in stats:
                cursor.execute("""
                    INSERT OR REPLACE INTO user_models (user_id, model_type, models)
                    VALUES (?, 'audio', ?)
                """, (user_id, str(stats["audio_models"])))
            
            conn.commit()

    @classmethod
    def get_instance(cls, db_file: str = "data/bot_data.db") -> 'DatabaseManager':
        """Получение единственного экземпляра класса DatabaseManager."""
        if cls._instance is None:
            cls._instance = DatabaseManager(db_file)
        return cls._instance

# Создаем глобальный экземпляр менеджера базы данных
db = DatabaseManager.get_instance() 