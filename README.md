# Aiogram 3 Bot Template

Готовый шаблон Telegram-бота на **aiogram 3** + **SQLite (aiosqlite)** + **Pydantic Settings**.

## Возможности
- 🏗 Чистая архитектура: `handlers` / `middlewares` / `database` / `keyboards` / `lexicon`
- 👤 Регистрация пользователей при `/start`
- 🔐 Админ-доступ через middleware (`is_admin` по `user_id` в БД или `ADMIN_IDS` в `.env`)
- 📊 Команда `/stats` — статистика пользователей и действий
- 📝 Логирование действий в SQLite
- ⚙️ Конфиг через `.env` (pydantic-settings)

## Структура проекта
```
├── bot.py                 # Точка входа
├── config.py              # Настройки (pydantic-settings)
├── lexicon.py             # Тексты ответов
├── requirements.txt
├── .env.example
├── .gitignore
├── database/
│   ├── __init__.py
│   ├── db.py              # Подключение к SQLite (aiosqlite)
│   └── repository.py      # CRUD: register, is_admin, log_action, get_stats
├── handlers/
│   ├── __init__.py
│   ├── start_handler.py   # /start
│   └── stats_handler.py   # /stats (только админы)
├── middlewares/
│   ├── __init__.py
│   └── admin.py           # Middleware проверки админа
└── keyboards/
    ├── __init__.py
    └── reply.py           # Reply-клавиатуры
```

## Быстрый старт

```bash
# 1. Клонируй
git clone https://github.com/L-MORIA/aiogram-bot-template.git
cd aiogram-bot-template

# 2. Виртуальное окружение
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Зависимости
pip install -r requirements.txt

# 4. Конфиг
cp .env.example .env
# отредактируй .env — вставь BOT_TOKEN и свои ADMIN_IDS

# 5. Запуск
python bot.py
```

## Переменные окружения (`.env`)
| Переменная | Описание | Пример |
|------------|----------|--------|
| `BOT_TOKEN` | Токен от @BotFather | `123456:ABC-DEF...` |
| `ADMIN_IDS` | Список Telegram ID админов через запятую | `123456789,987654321` |
| `DB_PATH` | Путь к SQLite файлу | `bot.db` |

## Как работает админство
1. При первом `/start` пользователь попадает в таблицу `users` с `is_admin=0`
2. Админы задаются двумя способами:
   - Через `ADMIN_IDS` в `.env` (сразу имеют доступ)
   - Через поле `is_admin=1` в БД (можно выдавать/забирать в runtime)
3. Middleware `AdminMiddleware` проверяет оба источника и кладёт `is_admin: bool` в `data` хендлера

## Команды бота
| Команда | Описание | Доступ |
|---------|----------|--------|
| `/start` | Регистрация / приветствие | Все |
| `/stats` | Статистика бота | Только админы |

## Схема БД (SQLite)
```sql
-- Users
CREATE TABLE users (
    user_id     INTEGER PRIMARY KEY,
    first_name  TEXT NOT NULL,
    username    TEXT UNIQUE,
    joined_at   TEXT DEFAULT CURRENT_TIMESTAMP,
    is_admin    INTEGER DEFAULT 0
);

-- Logs
CREATE TABLE bot_logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    action      TEXT NOT NULL,
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

## Дальнейшее развитие
- 🐳 `Dockerfile` + `docker-compose.yml`
- 🧪 Pytest-тесты для `repository` и `handlers`
- 🔄 Alembic миграции
- 📦 GitHub Actions CI (ruff + pytest)
- 🌐 Webhook-режим для продакшена

## Лицензия
MIT — используй как основу для своих ботов.