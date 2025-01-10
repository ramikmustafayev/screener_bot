from aiogram.types import KeyboardButton,ReplyKeyboardMarkup


def create_settings_kb():
    kb_list=[
        [KeyboardButton(text='Период пампа'),
        KeyboardButton(text='Процент пампа')],
        [KeyboardButton(text='Период дампа'),
        KeyboardButton(text='Процент дампа')]
    ]

    keyboard=ReplyKeyboardMarkup(keyboard=kb_list,resize_keyboard=True,one_time_keyboard=True)
    return keyboard


def create_cancel_keyboard():
    kb_list=[
        [KeyboardButton(text='Отмена'),]
    ]
    keyboard=ReplyKeyboardMarkup(keyboard=kb_list,resize_keyboard=True,one_time_keyboard=True)
    return keyboard