from aiogram.fsm.state import State, StatesGroup


class AddTask(StatesGroup):
    waiting_title = State()
    waiting_priority = State()
    waiting_due_date = State()


class EditTask(StatesGroup):
    waiting_new_title = State()
