from aiogram import Router,F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from services.liquidity_and_volatility_calculator import calculate_liquidity,calculate_volatility
from services.sma_calculator import calculate_sma50
from keyboards.all_keyboards import get_inline_kb,get_inline_back_kb,get_token_info_kb,create_cancel_keyboard
from database.models.tokens import Token
from client_api.crypto_rank import CryptoRankCLient
from client_api.bybit_api import BybitClient
from states.states import PumpState
callback_router=Router()

#{'spread(%)':round(spread,4),'buy_liq(1%)':round(buy_liq,2),'sell_liq(1%)':round(sell_liq,2),'total_liq':round(total_liq,2)}

@callback_router.callback_query(F.data.startswith('inline_'))
async def process_inline_callback(call:CallbackQuery,user,repo,config,state:FSMContext):
    tokens=repo.tokens
   
    user_id = user.id
    await call.answer()
    data,ticker=call.data.replace('inline_','').split(':')
    token:Token=await tokens.get_one_or_none(ticker=ticker,user_id=user_id)
    is_in_blacklist=token.is_in_blacklist
    is_interesting=token.is_interesting
    if data=='liquidity':
        liq=await calculate_liquidity(ticker)
        
        text=''
        for key,value in liq.items():
            text+=f'{value}:::'
        
        text=text[:-3]

        markup=get_inline_kb(ticker,liquidity=text)
        await call.message.edit_reply_markup(reply_markup=markup)
    
    elif data=='volatility':
        vol=await calculate_volatility(ticker)
        markup=get_inline_kb(ticker,volatility=str(vol))
        await call.message.edit_reply_markup(reply_markup=markup)

    elif data=='sma':
       
        sma=await calculate_sma50(ticker)
        
        markup=get_inline_kb(ticker,sma=sma)
        await call.message.edit_reply_markup(reply_markup=markup)

    elif data=='add_to_black_list':
        
        updated_token=await tokens.update({'ticker':ticker,'user_id':user_id},{'is_in_blacklist':not is_in_blacklist})
        markup=get_inline_kb(updated_token)
        await call.message.edit_reply_markup(reply_markup=markup)

    elif data=='inline_into_interesting':
        updated_token=await tokens.update({'ticker':ticker,'user_id':user_id},{'is_interesting':not is_interesting})
        markup=get_inline_kb(updated_token)
        await call.message.edit_reply_markup(reply_markup=markup)

    elif data=='add_to_black_list_info':
        updated_token:Token=await tokens.update({'ticker':ticker,'user_id':user_id},{'is_in_blacklist':not is_in_blacklist})
        markup=get_token_info_kb(updated_token)
        await call.message.edit_reply_markup(reply_markup=markup)

    elif data=='into_interesting_info':
        updated_obj:Token=await tokens.update({'ticker':ticker,'user_id':user_id},{'is_interesting':not is_interesting})
        markup=get_token_info_kb(updated_obj)
        await call.message.edit_reply_markup(reply_markup=markup)

    elif data=='info':
        
        client=CryptoRankCLient(config.api.crypto_rank_url)
        try:
            token_info=await client.get_token_info(ticker[:-4],config)
        finally:
            await client.close()

        text = f'''<b>Symbol:</b> {token_info.get('symbol', 'N/A')}
<b>Name:</b> {token_info.get('name', 'N/A')}
<b>Rank:</b> {token_info.get('rank', 'N/A')}
<b>Price:</b> ${float(token_info.get('price') or 0):.8f}
<b>Total Supply:</b> {int(token_info.get('totalSupply') or 0):,.0f}
<b>Max Supply:</b> {int(token_info.get('maxSupply') or 0):,.0f}
<b>Circulating Supply:</b> {int(token_info.get('circulatingSupply') or 0):,.0f}
<b>Market Cap:</b> ${float(token_info.get('marketCap') or 0):,.2f}
<b>ATH Value:</b> ${float(token_info.get('ath', {}).get('value') or 0):,.2f}
<b>ATH Percent Change:</b> {float(token_info.get('ath', {}).get('percentChange') or 0):,.2f}%
<b>ATL Value:</b> ${float(token_info.get('atl', {}).get('value') or 0):,.2f}
<b>ATL Percent Change:</b> {float(token_info.get('atl', {}).get('percentChange') or 0):,.2f}%
        '''
     
        await call.message.edit_text(text,reply_markup=get_inline_back_kb(ticker=ticker))
    elif data=='back':
        client=BybitClient(config.api.bybit_url)
        try:
            ticker_from_api=await client.fetch_token_info(ticker)
        finally:
            await client.close()
        last_pump_price=token.last_price
        current_price=float(ticker_from_api['lastPrice'])
        price_change_in_percent = ((current_price - last_pump_price) / last_pump_price) * 100
        await call.message.edit_text(f'''
                                ByBit — {token.pump_period} — <b>{ticker}</b>
<b>Pump</b>: {price_change_in_percent:.2f}% ({last_pump_price} - {current_price})
<b>Signal 24</b>: {token.sygnal_per_day}
                                ''',parse_mode='HTML',reply_markup=get_inline_kb(ticker_name=ticker,is_interesting=is_interesting,is_in_blacklist=is_in_blacklist))
    
    elif data=='change_pump_percent':
        await state.set_state(PumpState.pump_percent)
        await state.update_data(ticker=ticker)
        await call.message.answer(f'Введите новое значение для токена: {token.ticker}',reply_markup=create_cancel_keyboard())

    elif data=='change_pump_percent_all':
        await state.set_state(PumpState.pump_percent)
        await state.update_data(ticker='all')
        await call.message.answer('Введите новое значение для всех токенов:',reply_markup=create_cancel_keyboard())

    elif data=='chance_pump_period':
        await state.set_state(PumpState.pump_period)
        await call.message.answer('Введите новое значение для всех токенов:',reply_markup=create_cancel_keyboard())
    

    

    
        
  