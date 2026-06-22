from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)

router = Router(name="start")

MINI_APP_URL = "https://globewalkeruz.github.io/todosmart-bot/"

WELCOME = """
🎯 *Welcome to TodoSmart!*

Your personal task manager — now as a Telegram Mini App.

Tap the button below to open your tasks 👇
"""


def _open_app_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📱 Open TodoSmart",
                    web_app=WebAppInfo(url=MINI_APP_URL),
                )
            ]
        ]
    )


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(WELCOME, parse_mode="Markdown", reply_markup=_open_app_kb())


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Open @krill2lo\\_bot and tap *📱 Open TodoSmart* to manage your tasks.",
        parse_mode="Markdown",
        reply_markup=_open_app_kb(),
    )
