from aiogram.filters.callback_data import CallbackData


class TaskCB(CallbackData, prefix="t"):
    action: str   # view | complete | delete | edit | remind | assign
    task_id: str  # UUID


class PriorityCB(CallbackData, prefix="pri"):
    priority: str        # low | medium | high | urgent
    task_id: str = ""    # empty = selecting priority for new task


class ReminderCB(CallbackData, prefix="rem"):
    offset: str   # 1h | 3h | tomorrow | week | cancel
    task_id: str


class AssignCB(CallbackData, prefix="asgn"):
    task_id: str
    user_id: int


class NavCB(CallbackData, prefix="nav"):
    target: str   # main | my_tasks | group_tasks | stats | help | members | completed | add
    page: int = 0
