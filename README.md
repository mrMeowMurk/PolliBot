# 🤖 PolliBot

![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Telegram Bot](https://img.shields.io/badge/telegram-bot-blue.svg)

PolliBot - это мощный Telegram бот для взаимодействия с Pollinations.ai API, предоставляющий удобный интерфейс для генерации изображений и текста с использованием различных AI моделей.

<div align="center">
  <img src="preview.gif" alt="TypeNinja Preview" width="800"/>
</div>

## ✨ Возможности

- 🎨 **Генерация изображений** с использованием различных моделей
- 📝 **Генерация текста** с поддержкой изображений в запросах
- 🔄 **Выбор AI моделей** из доступного списка
- 📊 **Статистика использования** для каждого пользователя
- 🎯 **Удобный интерфейс** с inline-кнопками
- 💾 **Сохранение данных** в SQLite базе данных

## 🚀 Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/mrMeowMurk/PolliBot.git
cd nexusai-bot
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` в директории `config` и добавьте ваш токен бота:
```python
BOT_TOKEN = "ваш_токен_бота"
```

## 🛠 Использование

1. Запустите бота:
```bash
python bot.py
```

2. Найдите бота в Telegram по вашему тегу бота

3. Используйте команду `/start` для начала работы

## 📚 Структура проекта

```
nexusai-bot/
├── bot.py               # Основной файл бота
├── config/              # Конфигурация
│   └── config.py        # Настройки и константы
├── src/
│   ├── handlers/        # Обработчики команд
│   │   ├── ai/          # Обработчики AI функций
│   │   └── common/      # Общие обработчики
│   ├── keyboards/       # Клавиатуры и меню
│   ├── states/          # Состояния FSM
│   └── utils/           # Вспомогательные функции
└── requirements.txt     # Зависимости проекта
```

## 🔧 Технологии

- [Python](https://www.python.org/) 3.8+
- [aiogram](https://docs.aiogram.dev/) 3.x - современный фреймворк для Telegram ботов
- [Pollinations.ai API](https://pollinations.ai/) - API для генерации контента
- SQLite - для хранения данных пользователей

## 📝 Лицензия

Распространяется под лицензией MIT. Смотрите файл [LICENSE](LICENSE) для получения дополнительной информации.

## 🤝 Вклад в проект

Мы приветствуем ваш вклад в развитие проекта! Пожалуйста, создавайте issues и pull requests. 

## 📞 Поддержка

Если у вас возникли вопросы или проблемы:
- Напишите в Telegram: @MrMeowMurk

---

<div align="center">
Сделано с ❤️ MeowMurk
</div>
