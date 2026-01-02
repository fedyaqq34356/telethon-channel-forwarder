from aiogram.fsm.state import State, StatesGroup


class Account(StatesGroup):
    session_name = State()
    api_id = State()
    api_hash = State()
    phone = State()
    code = State()
    password = State()
    delete_choice = State()


class Channel(StatesGroup):
    source = State()
    target = State()
    delete_type = State()
    delete_choice = State()


class Link(StatesGroup):
    source = State()
    target = State()
    delete_choice = State()