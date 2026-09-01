from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.repository import get_stats, log_action

router = Router()

@router.message(Command("stats"))
async def cmd_stats(message: Message, is_admin: bool):
    if not is_admin:
        await message.answer("⛔ Доступно только админам")
        return
    await log_action(message.from_user.id, "/stats")
    stats = await get_stats()
    text = (
        f"📊 <b>Статистика бота</b>\n"
        f"👥 Всего пользователей: {stats['total_users']}\n"
        f"🟢 Активных сегодня: {stats['active_today']}\n"
        f"📈 Действия:\n"
    )
    for action, cnt in stats["actions"].items():
        text += f"  {action}: {cnt}\n"
    await message.answer(text, parse_mode="HTML")