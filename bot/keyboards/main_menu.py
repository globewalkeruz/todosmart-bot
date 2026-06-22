from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.keyboards.callback_data import NavCB


def main_menu_kb(is_group: bool = False) -> InlineKeyboardMarkup:
    if is_group:
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📝 Add Task",    callback_data=NavCB(target="add").pack()),
                InlineKeyboardButton(text="📋 Group Tasks", callback_data=NavCB(target="group_tasks").pack()),
            ],
            [
                InlineKeyboardButton(text="👥 Members",   callback_data=NavCB(target="members").pack()),
                InlineKeyboardButton(text="📊 Stats",     callback_data=NavCB(target="stats").pack()),
            ],
            [
                InlineKeyboardButton(text="❓ Help", callback_data=NavCB(target="help").pack()),
            ],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Add Task",  callback_data=NavCB(target="add").pack()),
            InlineKeyboardButton(text="📋 My Tasks",  callback_data=NavCB(target="my_tasks").pack()),
        ],
        [
            InlineKeyboardButton(text="✅ Completed", callback_data=NavCB(target="completed").pack()),
            InlineKeyboardButton(text="📊 Stats",     callback_data=NavCB(target="stats").pack()),
        ],
        [
            InlineKeyboardButton(text="❓ Help", callback_data=NavCB(target="help").pack()),
        ],
    ])
