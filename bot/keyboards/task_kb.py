from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.keyboards.callback_data import TaskCB, NavCB


def task_actions_kb(task_id: str, is_group: bool = False, is_completed: bool = False) -> InlineKeyboardMarkup:
    rows = []

    if not is_completed:
        if is_group:
            rows.append([
                InlineKeyboardButton(text="👥 Assign",   callback_data=TaskCB(action="assign",   task_id=task_id).pack()),
                InlineKeyboardButton(text="✅ Complete", callback_data=TaskCB(action="complete", task_id=task_id).pack()),
            ])
        else:
            rows.append([
                InlineKeyboardButton(text="✅ Complete", callback_data=TaskCB(action="complete", task_id=task_id).pack()),
                InlineKeyboardButton(text="⏰ Remind",   callback_data=TaskCB(action="remind",   task_id=task_id).pack()),
            ])
        rows.append([
            InlineKeyboardButton(text="✏️ Edit",      callback_data=TaskCB(action="edit",   task_id=task_id).pack()),
            InlineKeyboardButton(text="🏷️ Priority",  callback_data=TaskCB(action="priority", task_id=task_id).pack()),
        ])

    rows.append([
        InlineKeyboardButton(text="🗑️ Delete", callback_data=TaskCB(action="delete", task_id=task_id).pack()),
        InlineKeyboardButton(text="🔙 Back",   callback_data=NavCB(target="main").pack()),
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def task_list_kb(tasks: list[dict], page: int = 0, is_group: bool = False, show_completed: bool = False) -> InlineKeyboardMarkup:
    """Paginated task list — each task is a button that shows its detail."""
    from bot.keyboards.callback_data import TaskCB, NavCB

    PAGE_SIZE = 5
    start = page * PAGE_SIZE
    page_tasks = tasks[start: start + PAGE_SIZE]
    total_pages = (len(tasks) + PAGE_SIZE - 1) // PAGE_SIZE

    rows = []
    priority_icons = {"urgent": "🚨", "high": "🔴", "medium": "🟡", "low": "🟢"}
    for task in page_tasks:
        icon = priority_icons.get(task.get("priority", "medium"), "🟡")
        status = "✅ " if task.get("status") == "completed" else ""
        label = f"{status}{icon} {task['title'][:35]}"
        rows.append([InlineKeyboardButton(text=label, callback_data=TaskCB(action="view", task_id=task["task_id"]).pack())])

    # Pagination row
    nav_row = []
    if page > 0:
        target = "completed" if show_completed else ("group_tasks" if is_group else "my_tasks")
        nav_row.append(InlineKeyboardButton(text="◀️", callback_data=NavCB(target=target, page=page - 1).pack()))
    if page < total_pages - 1:
        target = "completed" if show_completed else ("group_tasks" if is_group else "my_tasks")
        nav_row.append(InlineKeyboardButton(text="▶️", callback_data=NavCB(target=target, page=page + 1).pack()))
    if nav_row:
        rows.append(nav_row)

    # Footer
    rows.append([
        InlineKeyboardButton(text="➕ Add Task", callback_data=NavCB(target="add").pack()),
        InlineKeyboardButton(text="🔙 Menu",    callback_data=NavCB(target="main").pack()),
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)
