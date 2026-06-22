from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from supabase import AsyncClient

from bot.keyboards.callback_data import NavCB, TaskCB, PriorityCB
from bot.keyboards.main_menu import main_menu_kb
from bot.keyboards.task_kb import task_actions_kb, task_list_kb
from bot.keyboards.priority_kb import priority_picker_kb
from bot.states.task_states import AddTask, EditTask
from bot.database.queries import tasks as tq
from bot.utils.formatters import fmt_task
from bot.utils.date_parser import parse_due_date

router = Router(name="tasks")


def _is_group(chat_type: str) -> bool:
    return chat_type in ("group", "supergroup", "channel")


# ── Add task flow ──────────────────────────────────────────────────────────────

@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext, db: AsyncClient) -> None:
    if message.text and len(message.text.split(maxsplit=1)) > 1:
        task_title = message.text.split(maxsplit=1)[1].strip()
        await _create_task_quick(message, task_title, state, db)
        return
    await state.set_state(AddTask.waiting_title)
    await message.answer(
        "📝 *Add New Task*\n\nSend me the task title:",
        parse_mode="Markdown",
    )


@router.callback_query(NavCB.filter(F.target == "add"))
async def cb_add_task(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AddTask.waiting_title)
    await query.message.edit_text(
        "📝 *Add New Task*\n\nSend me the task title:",
        parse_mode="Markdown",
    )
    await query.answer()


@router.message(AddTask.waiting_title)
async def fsm_got_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text.strip())
    await state.set_state(AddTask.waiting_priority)
    await message.answer(
        "🏷️ Choose a priority for this task:",
        reply_markup=priority_picker_kb(),
    )


@router.message(AddTask.waiting_due_date)
async def fsm_got_due_date(message: Message, state: FSMContext, db: AsyncClient) -> None:
    data = await state.get_data()
    due = parse_due_date(message.text or "skip")
    user_id = message.from_user.id
    is_grp = _is_group(message.chat.type)
    group_id = message.chat.id if is_grp else None

    task = await tq.create_task(
        db,
        title=data["title"],
        created_by=user_id,
        priority=data.get("priority", "medium"),
        group_id=group_id,
        due_date=due,
    )
    await state.clear()
    await message.answer(
        f"✅ *Task created!*\n\n{fmt_task(task)}",
        parse_mode="Markdown",
        reply_markup=main_menu_kb(is_grp),
    )


async def _create_task_quick(message: Message, title: str, state: FSMContext, db: AsyncClient) -> None:
    is_grp = _is_group(message.chat.type)
    group_id = message.chat.id if is_grp else None
    task = await tq.create_task(db, title=title, created_by=message.from_user.id, group_id=group_id)
    await state.clear()
    await message.answer(
        f"✅ *Task created!*\n\n{fmt_task(task)}",
        parse_mode="Markdown",
        reply_markup=main_menu_kb(is_grp),
    )


# ── List tasks ─────────────────────────────────────────────────────────────────

@router.message(Command("list"))
async def cmd_list(message: Message, db: AsyncClient) -> None:
    is_grp = _is_group(message.chat.type)
    if is_grp:
        tasks = await tq.list_group_tasks(db, message.chat.id)
        title = "📋 *Group Tasks*"
    else:
        tasks = await tq.list_personal_tasks(db, message.from_user.id)
        title = "📋 *Your Tasks*"

    if not tasks:
        await message.answer(
            f"{title}\n\n📭 No pending tasks! Use ➕ Add Task to create one.",
            parse_mode="Markdown",
            reply_markup=main_menu_kb(is_grp),
        )
        return

    await message.answer(
        f"{title} ({len(tasks)} pending)",
        parse_mode="Markdown",
        reply_markup=task_list_kb(tasks, is_group=is_grp),
    )


@router.callback_query(NavCB.filter(F.target == "my_tasks"))
async def cb_my_tasks(query: CallbackQuery, callback_data: NavCB, db: AsyncClient) -> None:
    tasks = await tq.list_personal_tasks(db, query.from_user.id)
    if not tasks:
        await query.message.edit_text(
            "📋 *Your Tasks*\n\n📭 No pending tasks!",
            parse_mode="Markdown",
            reply_markup=main_menu_kb(False),
        )
    else:
        await query.message.edit_text(
            f"📋 *Your Tasks* ({len(tasks)} pending)",
            parse_mode="Markdown",
            reply_markup=task_list_kb(tasks, page=callback_data.page),
        )
    await query.answer()


@router.callback_query(NavCB.filter(F.target == "completed"))
async def cb_completed(query: CallbackQuery, callback_data: NavCB, db: AsyncClient) -> None:
    tasks = await tq.list_personal_tasks(db, query.from_user.id, status="completed")
    if not tasks:
        await query.message.edit_text(
            "✅ *Completed Tasks*\n\n🎉 No completed tasks yet!",
            parse_mode="Markdown",
            reply_markup=main_menu_kb(False),
        )
    else:
        await query.message.edit_text(
            f"✅ *Completed Tasks* ({len(tasks)})",
            parse_mode="Markdown",
            reply_markup=task_list_kb(tasks, page=callback_data.page, show_completed=True),
        )
    await query.answer()


# ── View single task ───────────────────────────────────────────────────────────

@router.callback_query(TaskCB.filter(F.action == "view"))
async def cb_view_task(query: CallbackQuery, callback_data: TaskCB, db: AsyncClient) -> None:
    task = await tq.get_task(db, callback_data.task_id)
    if not task:
        await query.answer("Task not found.", show_alert=True)
        return
    is_grp = _is_group(query.message.chat.type)
    is_done = task.get("status") == "completed"
    await query.message.edit_text(
        fmt_task(task),
        parse_mode="Markdown",
        reply_markup=task_actions_kb(task["task_id"], is_group=is_grp, is_completed=is_done),
    )
    await query.answer()


# ── Complete task ──────────────────────────────────────────────────────────────

@router.callback_query(TaskCB.filter(F.action == "complete"))
async def cb_complete_task(query: CallbackQuery, callback_data: TaskCB, db: AsyncClient) -> None:
    await tq.complete_task(db, callback_data.task_id, query.from_user.id)
    is_grp = _is_group(query.message.chat.type)
    await query.message.edit_text(
        "✅ *Task completed!* Great work! 🎉",
        parse_mode="Markdown",
        reply_markup=main_menu_kb(is_grp),
    )
    await query.answer("Marked as complete!")


# ── Delete task ────────────────────────────────────────────────────────────────

@router.callback_query(TaskCB.filter(F.action == "delete"))
async def cb_delete_task(query: CallbackQuery, callback_data: TaskCB, db: AsyncClient) -> None:
    await tq.delete_task(db, callback_data.task_id)
    is_grp = _is_group(query.message.chat.type)
    await query.message.edit_text(
        "🗑️ *Task deleted.*",
        parse_mode="Markdown",
        reply_markup=main_menu_kb(is_grp),
    )
    await query.answer("Deleted.")


# ── Edit task title ────────────────────────────────────────────────────────────

@router.callback_query(TaskCB.filter(F.action == "edit"))
async def cb_edit_task(query: CallbackQuery, callback_data: TaskCB, state: FSMContext) -> None:
    await state.set_state(EditTask.waiting_new_title)
    await state.update_data(task_id=callback_data.task_id)
    await query.message.edit_text(
        "✏️ *Edit Task*\n\nSend the new title:",
        parse_mode="Markdown",
    )
    await query.answer()


@router.message(EditTask.waiting_new_title)
async def fsm_edit_title(message: Message, state: FSMContext, db: AsyncClient) -> None:
    data = await state.get_data()
    new_title = message.text.strip()
    await tq.update_task(db, data["task_id"], title=new_title)
    await state.clear()
    is_grp = _is_group(message.chat.type)
    await message.answer(
        f"✅ *Task updated!*\n\nNew title: {new_title}",
        parse_mode="Markdown",
        reply_markup=main_menu_kb(is_grp),
    )


# ── Change priority ────────────────────────────────────────────────────────────

@router.callback_query(TaskCB.filter(F.action == "priority"))
async def cb_change_priority(query: CallbackQuery, callback_data: TaskCB) -> None:
    await query.message.edit_text(
        "🏷️ *Change Priority*\n\nSelect a new priority:",
        parse_mode="Markdown",
        reply_markup=priority_picker_kb(task_id=callback_data.task_id),
    )
    await query.answer()


@router.callback_query(F.data.startswith("pri:"))
async def cb_priority_selected(query: CallbackQuery, state: FSMContext, db: AsyncClient) -> None:
    parts = query.data.split(":", 2)
    priority = parts[1] if len(parts) > 1 else "medium"
    task_id = parts[2] if (len(parts) > 2 and parts[2]) else ""

    current_state = await state.get_state()
    if current_state == AddTask.waiting_priority.state:
        await state.update_data(priority=priority)
        await state.set_state(AddTask.waiting_due_date)
        await query.answer()
        await query.message.edit_text(
            "📅 *Due date?* (optional)\n\nType: `tomorrow`, `next week`, `DD.MM.YYYY`, or `skip`",
            parse_mode="Markdown",
        )
        return
    if not task_id:
        await query.answer("Please start again from Add Task.", show_alert=True)
        return
    await tq.update_task(db, task_id, priority=priority)
    is_grp = _is_group(query.message.chat.type)
    await query.message.edit_text(
        f"🏷️ Priority updated to *{priority.title()}*!",
        parse_mode="Markdown",
        reply_markup=main_menu_kb(is_grp),
    )
    await query.answer("Priority updated!")
