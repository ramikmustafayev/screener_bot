from aiogram.types import KeyboardButton,ReplyKeyboardMarkup,InlineKeyboardButton,InlineKeyboardMarkup
from database.models.tokens import Token

def create_settings_kb():
    kb_list=[
        [KeyboardButton(text='Получить инфо о настройках токена')],
        [KeyboardButton(text='Период пампа'),
        KeyboardButton(text='Процент пампа')],     
    ]

    keyboard=ReplyKeyboardMarkup(keyboard=kb_list,resize_keyboard=True,one_time_keyboard=True)
    return keyboard


def create_cancel_keyboard():
    kb_list=[
        [KeyboardButton(text='Отмена'),]
    ]
    keyboard=ReplyKeyboardMarkup(keyboard=kb_list,resize_keyboard=True,one_time_keyboard=True)
    return keyboard

def get_inline_back_kb(ticker):
    kb_list=[
        [InlineKeyboardButton(text='Назад',callback_data=f'inline_back:{ticker}')]
    ]
    keyboard=InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard


def get_inline_kb(token:Token,volatility=None,liquidity=None,sma=None):
    is_in_blacklist=token.is_in_blacklist
    is_interesting=token.is_interesting
    ticker_name=token.ticker

    inline_kb_list=[
        [InlineKeyboardButton(text='Добавить в черный список' if is_in_blacklist==False else 'Удалить из черного списка'  ,callback_data=f'inline_add_to_black_list:{ticker_name}'),
        InlineKeyboardButton(text='Добавить в избранное' if is_interesting==False else 'Удалить из избранных',callback_data=f'inline_into_interesting:{ticker_name}')],
        [InlineKeyboardButton(text=f'SMA: {sma}' if sma is not None else 'Вычислить SMA',callback_data=f'inline_sma:{ticker_name}')],
        [InlineKeyboardButton(text=liquidity if liquidity is not None else 'Вычислить ликвидность',callback_data=f'inline_liquidity:{ticker_name}'),],
        [InlineKeyboardButton(text=volatility if volatility is not None else 'Вычислить волатильность',callback_data=f'inline_volatility:{ticker_name}'),],
        [InlineKeyboardButton(text='Информация о токене',callback_data=f'inline_info:{ticker_name}'),],
    ]
    markup=InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
    
    return markup

    
def get_token_info_kb(token:Token):
    is_in_blacklist=token.is_in_blacklist
    is_interesting=token.is_interesting
    ticker_name=token.ticker

    kb_list=[
        [InlineKeyboardButton(text='Добавить в черный список' if is_in_blacklist==False else 'Удалить из черного списка'  ,callback_data=f'inline_add_to_black_list_info:{ticker_name}')],
        [InlineKeyboardButton(text='Добавить в избранное' if is_interesting==False else 'Удалить из избранных',callback_data=f'inline_into_interesting_info:{ticker_name}')],
        [InlineKeyboardButton(text='Изменить процент пампа для токена',callback_data=f'inline_change_pump_percent:{ticker_name}')],
        [InlineKeyboardButton(text='Изменить процент пампа для всех токенов',callback_data=f'inline_change_pump_percent_all:{ticker_name}')],
        [InlineKeyboardButton(text='Изменить период пампа для всех токенов',callback_data=f'inline_chance_pump_period:{ticker_name}')],
    ]

    markup=InlineKeyboardMarkup(inline_keyboard=kb_list)
    
    return markup

