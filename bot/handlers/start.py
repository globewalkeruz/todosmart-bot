from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from bot.keyboards.main_menu import main_menu_kb
from bot.keyboards.callback_data import NavCB

router = Router(name="start")


def _is_group(chat_type: str) -> bool:
    return chat_type in ("group", "supergroup", "channel")


WELCOME_PERSONAL = """
🎯 *Welcome to TodoSmart!* ✨

Your personal task manager, right inside Telegram.

🚀 *What you can do:*
• 📝 Add tasks with priorities
• ⏰ Set real push reminders
• ✅ Track completions
• 📊 See your productivity stats
• 👥 Collaborate in groups

Use the menu below to get started 👇
"""

WELCOME_GROUP = """
🎯 *TodoSmart — Group Mode* 👥

Collaborative task management for your team.

🚀 *Group features:*
• 📝 Shared task board
• 👥 Assign tasks to members
• ✅ Track who completed what
• 📊 Group productivity stats

Use the menu below 👇
"""

HELP_TEXT = """
❓ *TodoSmart Help*

*Commands:*
• `/start` — Open main menu
• `/add <task>` — Quick-add a task
• `/list` — Show your tasks
• `/help` — This message

*Priorities:* 🚨 Urgent · 🔴 High · 🟡 Medium · 🟢 Low

*Reminders:* Real push notifications at your chosen time.

*Groups:* Add the bot to any group — it automatically switches to team mode with task assignment.
"""


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    is_grp = _is_group(message.chat.type)
    text = WELCOME_GROUP if is_grp else WELCOME_PERSONAL
    await message.answer(text, parse_mode="Markdown", reply_markup=main_menu_kb(is_grp))


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    is_grp = _is_group(message.chat.type)
    await message.answer(HELP_TEXT, parse_mode="Markdown", reply_markup=main_menu_kb(is_grp))


@router.callback_query(NavCB.filter(F.target == "main"))
async def cb_main_menu(query: CallbackQuery) -> None:
    is_grp = _is_group(query.message.chat.type)
    text = "🎯 *TodoSmart* — choose an option:" if not is_grp else "👥 *TodoSmart Group* — choose an option:"
    await query.message.edit_text(text, parse_mode="Markdown", reply_markup=main_menu_kb(is_grp))
    await query.answer()


@router.callback_query(NavCB.filter(F.target == "help"))
async def cb_help(query: CallbackQuery) -> None:
    is_grp = _is_group(query.message.chat.type)
    await query.message.edit_text(HELP_TEXT, parse_mode="Markdown", reply_markup=main_menu_kb(is_grp))
    await query.answer()
