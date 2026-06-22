from aiogram import Router, F
from aiogram.types import CallbackQuery
from supabase import AsyncClient

from bot.keyboards.callback_data import NavCB
from bot.keyboards.main_menu import main_menu_kb
from bot.database.queries.tasks import get_user_stats, get_group_stats
from bot.utils.formatters import fmt_stats

router = Router(name="stats")


@router.callback_query(NavCB.filter(F.target == "stats"))
async def cb_stats(query: CallbackQuery, db: AsyncClient) -> None:
    is_grp = query.message.chat.type in ("group", "supergroup", "channel")

    if is_grp:
        data = await get_group_stats(db, query.message.chat.id)
        text = fmt_stats(data, title="📊 Group Statistics")
    else:
        data = await get_user_stats(db, query.from_user.id)
        text = fmt_stats(data, title="📊 Your Statistics")

    await query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=main_menu_kb(is_grp),
    )
    await query.answer()
