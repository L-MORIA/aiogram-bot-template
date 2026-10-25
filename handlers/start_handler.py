from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from database.repository import log_action, register_user
from keyboards.reply import get_main_keyboard
from lexicon import LEXICON

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, is_admin: bool = False) -> None:
    if message.from_user is None:
        return
    await register_user(
        message.from_user.id,
        message.from_user.first_name,
        message.from_user.username,
    )
    await log_action(message.from_user.id, "/start")
    await message.answer(
        LEXICON["start"],
        reply_markup=get_main_keyboard(is_admin),
    )


@router.message(Command("help"))
@router.message(F.text == "📋 Помощь")
async def cmd_help(message: Message) -> None:
    if message.from_user is not None:
        await log_action(message.from_user.id, "help")
    await message.answer(LEXICON["help"])
