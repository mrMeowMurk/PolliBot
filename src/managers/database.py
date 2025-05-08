import sqlite3
import os
from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple

class DatabaseManager:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_file: str = "data/bot_data.db"):
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
                    last_used TIMESTAMP,
                    current_model TEXT,
                    model_type TEXT
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
            
            conn.commit()

    def get_user_stats(self, user_id: int) -> dict:
        """Получение статистики пользователя."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            # Проверяем существование пользователя
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                # Создаем нового пользователя
                cursor.execute(
                    "INSERT INTO users (user_id, images_generated, texts_generated) VALUES (?, 0, 0)",
                    (user_id,)
                )
                conn.commit()
                return {
                    "images_generated": 0,
                    "texts_generated": 0,
                    "last_used": None,
                    "current_model": None,
                    "model_type": None,
                    "text_models": None,
                    "image_models": None
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
                "last_used": user[3],
                "current_model": user[4],
                "model_type": user[5],
                "text_models": models.get("text"),
                "image_models": models.get("image")
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
                    last_used = ?,
                    current_model = ?,
                    model_type = ?
                WHERE user_id = ?
            """, (
                stats["images_generated"],
                stats["texts_generated"],
                stats.get("last_used"),
                stats.get("current_model"),
                stats.get("model_type"),
                user_id
            ))
            
            # Обновляем модели пользователя
            if stats.get("text_models"):
                self._update_user_models(cursor, user_id, "text", stats["text_models"])
            if stats.get("image_models"):
                self._update_user_models(cursor, user_id, "image", stats["image_models"])
            
            conn.commit()

    def _update_user_models(self, cursor: sqlite3.Cursor, user_id: int, model_type: str, models: List[str]) -> None:
        """Обновление моделей пользователя."""
        cursor.execute("""
            INSERT OR REPLACE INTO user_models (user_id, model_type, models)
            VALUES (?, ?, ?)
        """, (user_id, model_type, str(models)))

    @classmethod
    def get_instance(cls, db_file: str = "data/bot_data.db") -> 'DatabaseManager':
        """Получение единственного экземпляра класса DatabaseManager."""
        if cls._instance is None:
            cls._instance = DatabaseManager(db_file)
        return cls._instance

# Создаем глобальный экземпляр менеджера базы данных
db = DatabaseManager.get_instance() 