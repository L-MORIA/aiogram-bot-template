from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_main_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    buttons = [[KeyboardButton(text="📋 Помощь")]]
    if is_admin:
        buttons.append([KeyboardButton(text="📊 Статистика")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
