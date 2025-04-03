from aiogram import Router ,F
from aiogram.types import ReplyKeyboardRemove
from aiogram.types import Message
from states.states import TokenState,PumpState,TokenInfoState
from database.models.tokens import Token
from aiogram.fsm.context import FSMContext
from database.repo.requests import RequestsRepo
from services.track_prices import track_target_prices
from keyboards.all_keyboards import create_cancel_keyboard,get_token_info_kb
token_router = Router()


@token_router.message(F.text=='/add')
async def add_token(message:Message,state:FSMContext):
    await state.set_state(TokenState.token_name)
    await message.answer('Введите токен, таргет-цену и направление("+"-выше, "-"-ниже) через пробел',reply_markup=create_cancel_keyboard())

@token_router.message(TokenState.token_name)
async def process_add_token(message:Message,state:FSMContext,user,config,repo:RequestsRepo):
    data=message.text
    if len(data.split(' '))!=3:
        await message.answer('Введите данные согласно шаблону')
        return



    ticker,price,direction=data.split(' ')

    token_repo=repo.tokens
    watch_list_repo=repo.watchlist
    ticker=ticker.upper()+'USDT'
    token=await token_repo.get_one_or_none(ticker=ticker)

    if not token:
        await message.answer('Токен не торгуется на бирже Bybit')
        return

    await watch_list_repo.add(user_id=user.id,ticker=ticker,target_price=float(price),direction=direction)
    await message.answer('Токен успешно добавлен в список отслеживаемых',reply_markup=ReplyKeyboardRemove())
    await state.clear()
    await track_target_prices(message,repo,config,user)


@token_router.message(F.text=='/delete')
async def delete_token(message:Message,state:FSMContext):
    await state.set_state(TokenState.token_id)
    await message.answer('Введите ID токена',reply_markup=create_cancel_keyboard())


@token_router.message(TokenState.token_id)
async def process_delete_token(message:Message,state:FSMContext,user,repo:RequestsRepo):
    try:
        id = int(message.text)
    except ValueError:
        await message.answer('Введите корректный ID токена (целое число)')
        return
    repo=repo.watchlist
    row_count=await repo.delete({'user_id':user.id,'id':id})
    if row_count>0:
        await message.answer(f'Токен с идентификатором {id} успешно удален из списка отслеживаемых',reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(f'Токен с таким идентификатором не существует в списке отслеживаемых',reply_markup=ReplyKeyboardRemove())
    await state.set_state(None)

@token_router.message(F.text=='/list')
async def get_tokens_list(message:Message,user,repo:RequestsRepo):
    repo=repo.watchlist
    
    tokens=await repo.get_all(user_id=user.id)
    if not tokens:
        await message.answer('У вас нет отслеживаемых токенов')
    for token in tokens:
        await message.answer(f'id: {token.id} ticker: {token.ticker} target-price: {token.target_price} direction: {token.direction}')



@token_router.message(F.text=='/tokens_in_black_list')
async def tokens_in_black_list(message:Message,repo:RequestsRepo):
    tokens_in_black_list=''
    repo=repo.tokens
    tokens=await repo.get_all(is_in_blacklist=True)
    if not tokens:
        await message.answer('У вас нет токенов в черном списке')

    for token in tokens:
        tokens_in_black_list+=f'id: {token.id} ticker: {token.ticker}\n'
    
    await message.answer(tokens_in_black_list)



@token_router.message(F.text=='Отмена')
async def cancel(message:Message,state:FSMContext):
    await state.set_state(None)
    await message.answer('Отмена',reply_markup=ReplyKeyboardRemove())


@token_router.message(TokenState.token_name)
async def process_add_to_black_list(message:Message,state:FSMContext,user,repo:RequestsRepo):
    data=message.text
    ticker=data.upper()+'USDT'
    black_list_repo=repo.blacklist
    await black_list_repo.add(ticker=ticker)
    await message.answer('Токен успешно добавлен в черный список',reply_markup=ReplyKeyboardRemove())
    await state.set_state(None)



    

@token_router.message(F.text=='/token_info')
async def get_token_info(message:Message,state:FSMContext):
    await state.set_state(TokenInfoState.token_name)
    await message.answer('Введите название токена, чтобы получить информацию о токене',reply_markup=create_cancel_keyboard())  



@token_router.message(TokenInfoState.token_name)
async def process_get_token_info(message:Message,state:FSMContext,repo:RequestsRepo,user):
    data=message.text
    token_repo=repo.tokens
    ticker=data.upper()+'USDT'
    token:Token=await token_repo.get_one_or_none(ticker=ticker,user_id=user.id)

    if not token:
        await message.answer('Токен отсуствует в базе данных')
        return
    
    
    
    await message.answer(f'''Токен {token.ticker}
Процент пампа {token.pump_percent}%
Период пампа {token.pump_period} минут
В черном списке: {token.is_in_blacklist}
В избранном: {token.is_interesting}
''', parse_mode='HTML', reply_markup=get_token_info_kb(token))
    await message.answer('-----------------------------------------------------------------------',reply_markup=ReplyKeyboardRemove())
    
    await state.set_state(None)




@token_router.message(PumpState.pump_percent)
async def process_change_pump_percent(message:Message,repo:RequestsRepo,state:FSMContext,user):
    data=await state.get_data()
    ticker=data.get('ticker',None)

    try:
        percent = float(message.text)
    except ValueError:
        await message.answer('Введите корректное число')
        return

    

    if ticker is not None:
        if ticker=='all':
            await repo.tokens.update({'user_id':user.id},{'pump_percent':percent})
            await message.answer(f'Значение для всех токенов изменено на <b>{percent}</b>',reply_markup=ReplyKeyboardRemove())
            await state.set_state(None)
            await state.update_data(ticker=None)
        else:
            await repo.tokens.update({'user_id':user.id,'ticker':ticker},{'pump_percent':percent})
            await message.answer(f'Значение для токена <b>{ticker}</b> изменено на <b>{percent}</b>',reply_markup=ReplyKeyboardRemove())
            await state.set_state(None)
            await state.update_data(ticker=None)
    else:
        await state.set_state(None)
        await state.update_data(ticker=None)
        await message.answer('Ошибка при извлечении данных',reply_markup=ReplyKeyboardRemove())

    







