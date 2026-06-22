from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.keyboards.callback_data import PriorityCB, NavCB

PRIORITIES = [
    ("🚨 Urgent", "urgent"),
    ("🔴 High",   "high"),
    ("🟡 Medium", "medium"),
    ("🟢 Low",    "low"),
]


def priority_picker_kb(task_id: str = "") -> InlineKeyboardMarkup:
    """Used both for new tasks (task_id='') and updating existing ones."""
    rows = [
        [InlineKeyboardButton(text=label, callback_data=PriorityCB(priority=val, task_id=task_id).pack())]
        for label, val in PRIORITIES
    ]
    rows.append([InlineKeyboardButton(text="🔙 Back", callback_data=NavCB(target="main").pack())])
    return InlineKeyboardMarkup(inline_keyboard=rows)
