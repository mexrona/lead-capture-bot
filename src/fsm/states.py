from aiogram.fsm.state import State, StatesGroup


class LeadFormStates(StatesGroup):
    idle = State()
    type_selection = State()
    budget_selection = State()
    deadline_selection = State()
    name_input = State()
    contact_input = State()
    comment_input = State()
    review = State()
    edit_menu = State()
    processing = State()
    finish = State()
    cancelled = State()
