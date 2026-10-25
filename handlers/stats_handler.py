import html

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from database.repository import get_stats, log_action

router = Router()


@router.message(Command("stats"))
@router.message(F.text == "📊 Статистика")
async def cmd_stats(message: Message, is_admin: bool = False):
    if not is_admin:
        await message.answer("⛔ Доступно только админам")
        return
    if message.from_user is not None:
        await log_action(message.from_user.id, "/stats")
    stats = await get_stats()
    text = (
        f"📊 <b>Статистика бота</b>\n"
        f"👥 Всего пользователей: {stats['total_users']}\n"
        f"🟢 Активных сегодня: {stats['active_today']}\n"
        f"📈 Действия:\n"
    )
    # action может содержать пользовательский ввод — экранируем HTML
    for action, cnt in stats["actions"].items():
        text += f"  {html.escape(str(action))}: {cnt}\n"
    await message.answer(text, parse_mode="HTML")
