from aiogram.fsm.state import State, StatesGroup

class PumpState(StatesGroup):
    pump_period =State()
    pump_percent=State()
    pump_percent_all=State()


class TokenState(StatesGroup):
    token_name =State()
    token_id =State()


class TokenInfoState(StatesGroup):
    token_name =State()
    token_id =State()



