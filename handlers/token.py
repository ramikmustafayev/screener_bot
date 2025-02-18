from aiogram import Router ,F
from aiogram.types import ReplyKeyboardRemove
from aiogram.types import Message
from states.states import TokenState,BlackListState
from aiogram.fsm.context import FSMContext
from database.repo.requests import RequestsRepo
from services.track_prices import track_target_prices
from keyboards.all_keyboards import create_cancel_keyboard
token_router = Router()


@token_router.message(F.text=='/add')
async def add_token(message:Message,state:FSMContext):
    await state.set_state(TokenState.token_name)
    await message.answer('Введите токен, таргет-цену и направление("+"-выше, "-"-ниже) через пробел',reply_markup=create_cancel_keyboard())


@token_router.message(F.text=='/add_to_black_list')
async def add_token(message:Message,state:FSMContext):
    await state.set_state(BlackListState.token_name)
    await message.answer('Введите название токена',reply_markup=create_cancel_keyboard())

@token_router.message(F.text=='/tokens_in_black_list')
async def tokens_in_black_list(message:Message,repo:RequestsRepo):
    repo=repo.blacklist
    
    tokens=await repo.get_all()
    for token in tokens:
        await message.answer(f'id: {token.id} ticker: {token.ticker}')



@token_router.message(F.text=='Отмена')
async def cancel(message:Message,state:FSMContext):
    await state.set_state(None)
    await message.answer('Отмена',reply_markup=ReplyKeyboardRemove())


@token_router.message(BlackListState.token_name)
async def process_add_to_black_list(message:Message,state:FSMContext,user,repo:RequestsRepo):
    data=message.text
    ticker=data.upper()+'USDT'
    black_list_repo=repo.blacklist
    await black_list_repo.add(ticker=ticker)
    await message.answer('Токен успешно добавлен в черный список')
    await state.set_state(None)


@token_router.message(TokenState.token_name)
async def process_add_token(message:Message,state:FSMContext,user,config,repo:RequestsRepo):
    data=message.text
    if len(data.split(' '))!=3:
        await message.answer('Введите данные согласно шаблону')
        return



    ticker,price,direction=data.split(' ')

    token_repo=repo.pump_tokens
    watch_list_repo=repo.watchlist
    ticker=ticker.upper()+'USDT'
    token=await token_repo.get_one_or_none(ticker=ticker)

    if not token:
        await message.answer('Токен не торгуется на бирже Bybit')
        return

    await watch_list_repo.add(user_id=user.id,ticker=ticker,target_price=float(price),direction=direction)
    await message.answer('Токен успешно добавлен в список отслеживаемых')
    await state.clear()
    await track_target_prices(message,repo,config,user)
    

    








@token_router.message(F.text=='/delete')
async def delete_token(message:Message,state:FSMContext):
    await state.set_state(TokenState.token_id)
    await message.answer('Введите ID токена')


@token_router.message(TokenState.token_id)
async def process_delete_token(message:Message,state:FSMContext,session,user,repo:RequestsRepo):
    id=int(message.text)
    repo=repo.watchlist
    await repo.delete({'user_id':user.id,'id':id})
    await message.answer(f'Token with id {id} succesfully deleted')
    await state.clear()




@token_router.message(F.text=='/list')
async def get_tokens_list(message:Message,user,repo:RequestsRepo):
    repo=repo.watchlist
    
    tokens=await repo.get_all_by_user_id(user_id=user.id)
    for token in tokens:
        await message.answer(f'id: {token.id} ticker: {token.ticker} target-price: {token.target_price} direction: {token.direction}')