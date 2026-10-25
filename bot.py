import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from config import config
from database.db import init_db
from handlers import start_handler, stats_handler
from middlewares.admin import AdminMiddleware

logging.basicConfig(level=logging.INFO)


async def main():
    await init_db()
    dp = Dispatcher()
    dp.message.middleware(AdminMiddleware())
    dp.include_router(start_handler.router)
    dp.include_router(stats_handler.router)

    # async with гарантирует закрытие сессии бота при любом исходе
    async with Bot(token=config.bot_token, parse_mode=ParseMode.HTML) as bot:
        logging.info("Bot started")
        await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped")
