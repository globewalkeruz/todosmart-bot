from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.keyboards.callback_data import ReminderCB, NavCB


def reminder_picker_kb(task_id: str) -> InlineKeyboardMarkup:
    options = [
        ("⏰ In 1 hour",    "1h"),
        ("⏰ In 3 hours",   "3h"),
        ("🌅 Tomorrow 9am", "tomorrow"),
        ("📅 Next week",    "week"),
    ]
    rows = [
        [InlineKeyboardButton(text=label, callback_data=ReminderCB(offset=val, task_id=task_id).pack())]
        for label, val in options
    ]
    rows.append([
        InlineKeyboardButton(text="❌ Cancel reminder", callback_data=ReminderCB(offset="cancel", task_id=task_id).pack()),
        InlineKeyboardButton(text="🔙 Back",            callback_data=NavCB(target="main").pack()),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)
