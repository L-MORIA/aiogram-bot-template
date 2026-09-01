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
    bot = Bot(token=config.bot_token, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.message.middleware(AdminMiddleware())
    dp.include_router(start_handler.router)
    dp.include_router(stats_handler.router)

    logging.info("Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped")