from __future__ import annotations
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from supabase import AsyncClient

from bot.keyboards.callback_data import NavCB, TaskCB, AssignCB
from bot.keyboards.main_menu import main_menu_kb
from bot.keyboards.task_kb import task_list_kb
from bot.database.queries import tasks as tq
from bot.database.queries.groups import get_members
from bot.utils.formatters import fmt_task

router = Router(name="groups")


@router.callback_query(NavCB.filter(F.target == "group_tasks"))
async def cb_group_tasks(query: CallbackQuery, callback_data: NavCB, db: AsyncClient) -> None:
    tasks = await tq.list_group_tasks(db, query.message.chat.id)
    if not tasks:
        await query.message.edit_text(
            "📋 *Group Tasks*\n\n📭 No pending tasks! Use ➕ Add Task to create one.",
            parse_mode="Markdown",
            reply_markup=main_menu_kb(True),
        )
    else:
        await query.message.edit_text(
            f"📋 *Group Tasks* ({len(tasks)} pending)",
            parse_mode="Markdown",
            reply_markup=task_list_kb(tasks, page=callback_data.page, is_group=True),
        )
    await query.answer()


@router.callback_query(NavCB.filter(F.target == "members"))
async def cb_group_members(query: CallbackQuery, db: AsyncClient) -> None:
    members = await get_members(db, query.message.chat.id)
    if not members:
        text = "👥 *Group Members*\n\nNo members found yet."
    else:
        lines = ["👥 *Group Members*\n"]
        for m in members:
            u = m.get("users") or {}
            name = u.get("first_name") or u.get("username") or f"User {m['user_id']}"
            role = m.get("role", "member")
            lines.append(f"• {'👑' if role == 'admin' else '👤'} {name} — {role}")
        text = "\n".join(lines)

    await query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=main_menu_kb(True),
    )
    await query.answer()


@router.callback_query(TaskCB.filter(F.action == "assign"))
async def cb_assign_task(query: CallbackQuery, callback_data: TaskCB, db: AsyncClient) -> None:
    members = await get_members(db, query.message.chat.id)
    if not members:
        await query.answer("No members found in this group.", show_alert=True)
        return

    buttons = []
    for m in members[:10]:
        u = m.get("users") or {}
        name = u.get("first_name") or u.get("username") or f"User {m['user_id']}"
        buttons.append([InlineKeyboardButton(
            text=f"👤 {name}",
            callback_data=AssignCB(task_id=callback_data.task_id, user_id=m["user_id"]).pack(),
        )])
    buttons.append([InlineKeyboardButton(text="🔙 Back", callback_data=NavCB(target="main").pack())])

    await query.message.edit_text(
        "👥 *Assign Task*\n\nSelect a member:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await query.answer()


@router.callback_query(AssignCB.filter())
async def cb_do_assign(query: CallbackQuery, callback_data: AssignCB, db: AsyncClient) -> None:
    await tq.assign_task(db, callback_data.task_id, callback_data.user_id, query.from_user.id)
    await query.message.edit_text(
        "✅ *Task assigned!*",
        parse_mode="Markdown",
        reply_markup=main_menu_kb(True),
    )
    await query.answer("Assigned!")
