from aiogram.fsm.state import State, StatesGroup

class PumpState(StatesGroup):
    pump_period =State()
    pump_percent=State()
    


class DumpState(StatesGroup):
    dump_period =State()
    dump_percent =State()


class TokenState(StatesGroup):
    token_name =State()
    token_id =State()

class BlackListState(StatesGroup):
    token_name =State()
    token_id =State()
    