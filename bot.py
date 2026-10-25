import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault

from config import config
from database.db import init_db
from database.repository import cleanup_old_logs
from handlers import start_handler, stats_handler
from middlewares.admin import AdminMiddleware
from middlewares.throttle import ThrottlingMiddleware

logging.basicConfig(level=logging.INFO)


async def set_bot_commands(bot: Bot) -> None:
    """Меню команд: базовое всем, /stats — только админам из ADMIN_IDS."""
    base_commands = [
        BotCommand(command="start", description="Регистрация и приветствие"),
        BotCommand(command="help", description="Помощь"),
    ]
    admin_commands = base_commands + [
        BotCommand(command="stats", description="Статистика бота"),
    ]
    await bot.set_my_commands(base_commands, scope=BotCommandScopeDefault())
    for admin_id in config.admin_ids:
        try:
            await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=admin_id))
        except TelegramBadRequest:
            # чат ещё не открывался — команды появятся после первого /start
            logging.debug("Не удалось задать команды для админа %s", admin_id)


async def main():
    await init_db()
    deleted = await cleanup_old_logs(config.log_retention_days)
    if deleted:
        logging.info("Удалено старых логов: %s", deleted)

    dp = Dispatcher()
    # порядок важен: AdminMiddleware кладёт is_admin в data,
    # ThrottlingMiddleware по нему пропускает админов
    dp.message.middleware(AdminMiddleware())
    dp.message.middleware(ThrottlingMiddleware())
    dp.include_router(start_handler.router)
    dp.include_router(stats_handler.router)

    # async with гарантирует закрытие сессии бота при любом исходе
    async with Bot(token=config.bot_token, parse_mode=ParseMode.HTML) as bot:
        await set_bot_commands(bot)
        logging.info("Bot started")
        await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped")
