from aiogram.fsm.state import State, StatesGroup

class EmaState(StatesGroup):

    ema_percent=State()
    


class TokenState(StatesGroup):
    token_name =State()
    token_id =State()



class SQLQueryState(StatesGroup):
    waiting_for_query = State()


class TokenInfoState(StatesGroup):
    token_name =State()
    token_id =State()
    token_timeframe=State()



