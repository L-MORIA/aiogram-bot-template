# Aiogram 3 Bot Template

[![CI](https://github.com/L-MORIA/aiogram-bot-template/actions/workflows/ci.yml/badge.svg)](https://github.com/L-MORIA/aiogram-bot-template/actions/workflows/ci.yml)

Готовый шаблон Telegram-бота на **aiogram 3** + **SQLite (aiosqlite)** + **Pydantic Settings**.

> Требуется **Python 3.10+** (код использует синтаксис `int | None`).

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
├── requirements-dev.txt   # pytest, pytest-asyncio, ruff
├── pyproject.toml         # конфиг pytest + ruff
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── .gitignore
├── database/
│   ├── __init__.py
│   ├── db.py              # Подключение к SQLite (aiosqlite)
│   └── repository.py      # CRUD: register, is_admin, log_action, get_stats, cleanup
├── handlers/
│   ├── __init__.py
│   ├── start_handler.py   # /start, /help
│   └── stats_handler.py   # /stats (только админы)
├── middlewares/
│   ├── __init__.py
│   ├── admin.py           # Проверка админа (ADMIN_IDS + БД)
│   └── throttle.py        # Anti-flood
├── keyboards/
│   ├── __init__.py
│   └── reply.py           # Reply-клавиатуры
├── tests/                 # pytest-тесты
└── .github/workflows/     # CI: ruff + pytest
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

### Запуск в Docker

```bash
cp .env.example .env   # вставь BOT_TOKEN и ADMIN_IDS
docker compose up -d --build

# логи / остановка
docker compose logs -f
docker compose down
```

База хранится в именованном томе `bot-data` и переживает пересборку; контейнер работает от непривилегированного пользователя и рестартуется автоматически (`restart: unless-stopped`).

## Разработка

```bash
# тесты и линтер
pip install -r requirements-dev.txt
pytest -v
ruff check .
```

CI (GitHub Actions) прогоняет `ruff` + `pytest` на Python 3.10–3.12 при каждом пуше.

## Что ещё встроено

- 🚦 **ThrottlingMiddleware** — anti-flood (1 сообщение / 0.5 сек, админы без ограничений)
- 🧹 **Ротация логов** — при старте удаляются записи `bot_logs` старше `LOG_RETENTION_DAYS` дней
- 📋 **Меню команд** — `set_my_commands` при старте: `/start`, `/help` всем, `/stats` — админам

## Переменные окружения (`.env`)
| Переменная | Описание | Пример |
|------------|----------|--------|
| `BOT_TOKEN` | Токен от @BotFather | `123456:ABC-DEF...` |
| `ADMIN_IDS` | Список Telegram ID админов через запятую (или JSON-списком) | `123456789,987654321` |
| `DB_PATH` | Путь к SQLite файлу | `bot.db` |
| `LOG_RETENTION_DAYS` | Сколько дней хранить `bot_logs` (0 = не удалять) | `30` |

## Как работает админство
1. При первом `/start` пользователь попадает в таблицу `users` с `is_admin=0`
2. Админы задаются двумя способами:
   - Через `ADMIN_IDS` в `.env` (сразу имеют доступ)
   - Через поле `is_admin=1` в БД (можно выдавать/забирать в runtime)
3. Middleware `AdminMiddleware` проверяет оба источника и кладёт `is_admin: bool` в `data` хендлера

## Команды бота
| Команда | Описание | Доступ |
|---------|----------|--------|
| `/start` | Регистрация / приветствие + главная клавиатура | Все |
| `/help` | Помощь (или кнопка «📋 Помощь») | Все |
| `/stats` | Статистика бота (или кнопка «📊 Статистика») | Только админы |

## Схема БД (SQLite)
```sql
-- Users
CREATE TABLE users (
    user_id     INTEGER PRIMARY KEY,
    first_name  TEXT NOT NULL,
    username    TEXT,
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

> Примечание: `username` без `UNIQUE` — юзернеймы Telegram меняются и могут быть
> заняты разными пользователями в разное время; `ON CONFLICT`-upsert при
> повторном `/start` обновляет `first_name` и `username`. Проверка внешних ключей
> включается через `PRAGMA foreign_keys = ON` в каждом соединении.

## Дальнейшее развитие
- 🔄 Alembic миграции
- 🌐 Webhook-режим для продакшена

## Лицензия
MIT — используй как основу для своих ботов.