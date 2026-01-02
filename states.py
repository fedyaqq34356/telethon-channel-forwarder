from aiogram.fsm.state import State, StatesGroup


class AddAccount(StatesGroup):
    waiting_session_name = State()
    waiting_api_id = State()
    waiting_api_hash = State()
    waiting_phone = State()
    waiting_code = State()
    waiting_password = State()


class AddSourceChannel(StatesGroup):
    waiting_username = State()


class AddTargetChannel(StatesGroup):
    waiting_username = State()


class DeleteChannel(StatesGroup):
    choosing_type = State()
    choosing_channel = State()


class LinkChannels(StatesGroup):
    choosing_source = State()
    choosing_target = State()