from datetime import datetime
from aiogram import Router,F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from keyboards.all_keyboards import get_inline_kb,get_token_info_kb,create_cancel_keyboard
from database.models.tokens import Token
from states.states import EmaState,TokenInfoState

callback_router=Router()



@callback_router.callback_query(F.data.startswith('inline_'))
async def process_inline_callback(call:CallbackQuery,user,repo,state:FSMContext):
    tokens=repo.tokens
   
    user_id = user.id
    await call.answer()
    data,ticker=call.data.replace('inline_','').split(':')
    token:Token=await tokens.get_one_or_none(ticker=ticker,user_id=user_id)
    is_in_blacklist=token.is_in_blacklist
    is_muted=token.is_muted

    



    if data=='add_to_black_list':
        
        updated_token=await tokens.update({'ticker':ticker,'user_id':user_id},{'is_in_blacklist':not is_in_blacklist})
        markup=get_inline_kb(updated_token)
        await call.message.edit_reply_markup(reply_markup=markup)

    elif data=='into_muted':
        current_time = datetime.now()
        updated_token=await tokens.update({'ticker':ticker,'user_id':user_id},{'is_muted':not is_muted,'updated_at':current_time})
        markup=get_inline_kb(updated_token)
        await call.message.edit_reply_markup(reply_markup=markup)

    elif data=='add_to_black_list_info':
        updated_token:Token=await tokens.update({'ticker':ticker,'user_id':user_id},{'is_in_blacklist':not is_in_blacklist})
        markup=get_token_info_kb(updated_token)
        await call.message.edit_reply_markup(reply_markup=markup)


    
    elif data=='change_ema_percent':
        await state.set_state(EmaState.ema_percent)
        await state.update_data(ticker=ticker)
        await call.message.answer(f'Введите новое значение для токена: {token.ticker}',reply_markup=create_cancel_keyboard())

    elif data=='change_ema_percent_all':
        await state.set_state(EmaState.ema_percent)
        await state.update_data(ticker='all')
        await call.message.answer(f'Введите новое значение для всех токенов',reply_markup=create_cancel_keyboard())
    elif data=='change_timeframe':
        await state.set_state(TokenInfoState.token_timeframe)
        await state.update_data(ticker=ticker)
        await call.message.answer(f'Введите новое значение для токена: {token.ticker}',reply_markup=create_cancel_keyboard())
    elif data=='change_timeframe_all':
        await state.set_state(TokenInfoState.token_timeframe)
        await state.update_data(ticker='all')
        await call.message.answer('Введите новое значение для всех токенов',reply_markup=create_cancel_keyboard())

    
    
    
        
  
