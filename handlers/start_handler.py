from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from database.repository import register_user, log_action
from lexicon import LEXICON

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await register_user(message.from_user.id, message.from_user.first_name, message.from_user.username)
    await log_action(message.from_user.id, "/start")
    await message.answer(LEXICON["start"])