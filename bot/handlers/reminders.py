from __future__ import annotations
from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery
from supabase import AsyncClient

from bot.keyboards.callback_data import TaskCB, ReminderCB, NavCB
from bot.keyboards.main_menu import main_menu_kb
from bot.keyboards.reminder_kb import reminder_picker_kb
from bot.database.queries import tasks as tq
from bot.database.queries.reminders import set_reminder, clear_reminder
from bot.scheduler.jobs import schedule_reminder, cancel_reminder
from bot.utils.date_parser import compute_reminder_offset

router = Router(name="reminders")


@router.callback_query(TaskCB.filter(F.action == "remind"))
async def cb_set_remind(query: CallbackQuery, callback_data: TaskCB, db: AsyncClient) -> None:
    task = await tq.get_task(db, callback_data.task_id)
    if not task:
        await query.answer("Task not found.", show_alert=True)
        return
    await query.message.edit_text(
        f"⏰ *Set Reminder*\n\n📝 {task['title']}\n\nChoose when to be reminded:",
        parse_mode="Markdown",
        reply_markup=reminder_picker_kb(callback_data.task_id),
    )
    await query.answer()


@router.callback_query(ReminderCB.filter())
async def cb_reminder_chosen(
    query: CallbackQuery, callback_data: ReminderCB, db: AsyncClient, bot: Bot
) -> None:
    is_grp = query.message.chat.type in ("group", "supergroup", "channel")

    if callback_data.offset == "cancel":
        task = await tq.get_task(db, callback_data.task_id)
        if task and task.get("reminder_job_id"):
            cancel_reminder(task["reminder_job_id"])
        await clear_reminder(db, callback_data.task_id)
        await query.message.edit_text(
            "🔕 Reminder cancelled.",
            reply_markup=main_menu_kb(is_grp),
        )
        await query.answer("Reminder cancelled.")
        return

    run_at = compute_reminder_offset(callback_data.offset)
    if not run_at:
        await query.answer("Invalid option.", show_alert=True)
        return

    task = await tq.get_task(db, callback_data.task_id)
    if not task:
        await query.answer("Task not found.", show_alert=True)
        return

    # Cancel existing job if any
    if task.get("reminder_job_id"):
        cancel_reminder(task["reminder_job_id"])

    # Always DM the reminder to the user, even if set from a group
    chat_id = query.from_user.id
    job_id = schedule_reminder(bot, chat_id, callback_data.task_id, task["title"], run_at)
    await set_reminder(db, callback_data.task_id, run_at, job_id)

    await query.message.edit_text(
        f"⏰ *Reminder set!*\n\n📝 {task['title']}\n🕐 {run_at.strftime('%d %b %Y at %H:%M')}",
        parse_mode="Markdown",
        reply_markup=main_menu_kb(is_grp),
    )
    await query.answer("Reminder set!")
