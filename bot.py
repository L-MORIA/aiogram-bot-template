import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
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
logger = logging.getLogger(__name__)


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
            await bot.set_my_commands(
                admin_commands, scope=BotCommandScopeChat(chat_id=admin_id)
            )
        except TelegramBadRequest:
            # чат ещё не открывался — команды появятся после первого /start
            logger.debug("Не удалось задать команды для админа %s", admin_id)


async def main() -> None:
    await init_db()
    deleted = await cleanup_old_logs(config.log_retention_days)
    if deleted:
        logger.info("Удалено старых логов: %s", deleted)

    dp = Dispatcher()
    # порядок важен: AdminMiddleware кладёт is_admin в data,
    # ThrottlingMiddleware по нему пропускает админов
    dp.message.middleware(AdminMiddleware())
    dp.message.middleware(ThrottlingMiddleware())
    dp.include_router(start_handler.router)
    dp.include_router(stats_handler.router)

    # parse_mode как kwarg Bot() удалён в aiogram 3.7 — только DefaultBotProperties.
    async with Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    ) as bot:
        # Если бот раньше работал на webhook, start_polling упадёт с 409 Conflict,
        # пока вебхук не снят.
        await bot.delete_webhook(drop_pending_updates=True)
        await set_bot_commands(bot)
        logger.info("Bot started")
        await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
