from aiogram.types import KeyboardButton,ReplyKeyboardMarkup,InlineKeyboardButton,InlineKeyboardMarkup
from database.models.tokens import Token



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


def get_inline_kb(token:Token):
    is_in_blacklist=token.is_in_blacklist
    is_muted=token.is_muted
    ticker_name=token.ticker

    inline_kb_list=[
        [InlineKeyboardButton(text='Добавить в черный список' if is_in_blacklist==False else 'Удалить из черного списка'  ,callback_data=f'inline_add_to_black_list:{ticker_name}')],
        [InlineKeyboardButton(text='Заглушить на 15 мин' if is_muted==False else 'Убрать из заглушенных',callback_data=f'inline_into_muted:{ticker_name}')],
        [InlineKeyboardButton(text='Информация о токене',callback_data=f'inline_info:{ticker_name}'),],
    ]
    markup=InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
    
    return markup

    
def get_token_info_kb(token:Token):
    is_in_blacklist=token.is_in_blacklist
    ticker_name=token.ticker

    kb_list=[
        [InlineKeyboardButton(text='Добавить в черный список' if is_in_blacklist==False else 'Удалить из черного списка'  ,callback_data=f'inline_add_to_black_list_info:{ticker_name}')],
        [InlineKeyboardButton(text='Изменить процент пампа для токена',callback_data=f'inline_change_pump_percent:{ticker_name}')],
        [InlineKeyboardButton(text='Изменить процент пампа для всех токенов',callback_data=f'inline_change_pump_percent_all:{ticker_name}')],
        
    ]

    markup=InlineKeyboardMarkup(inline_keyboard=kb_list)
    
    return markup

