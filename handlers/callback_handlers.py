import typing
from aiogram.types import InputMediaPhoto,BufferedInputFile
from datetime import datetime
from aiogram import Router,F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from services.sma_calculator import calculate_sma50
from keyboards.all_keyboards import get_inline_kb,get_inline_back_kb,get_token_info_kb,create_cancel_keyboard
from database.models.tokens import Token
from client_api.crypto_rank import CryptoRankCLient
from client_api.bybit_api import BybitClient
from states.states import PumpState
from services.generate_chart import prepare_dataframe,generate_chart

callback_router=Router()

if typing.TYPE_CHECKING:
    from aiogram import Bot


@callback_router.callback_query(F.data.startswith('inline_'))
async def process_inline_callback(call:CallbackQuery,user,repo,config,state:FSMContext):
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



    elif data=='info':
        try:
            bybit_url=config.api.bybit_url
            bybit_client=BybitClient(bybit_url)
            result=await bybit_client.fetch_klines(ticker, '15', 100)
        finally:
            await bybit_client.close()

        raw_data = result['list']
        if len(raw_data) >= 2:
            last_volume = float(raw_data[0][5])
            previous_volume = float(raw_data[1][5])
            volume_change_percent = ((last_volume - previous_volume) / previous_volume) * 100
        raw_data = raw_data[::-1]
        df = prepare_dataframe(raw_data)
        
       
        
        symbol=token.ticker
        rank=token.rank
        total_supply=token.total_supply
        circulating_supply=token.circulating_supply
        market_cap=token.market_cap
        ath_value=token.ath_value
        atl_value=token.atl_value

        chart_buf = generate_chart(df)

        text = f'''<b>Symbol:</b> {symbol}
<b>Volume Change In Percent</b> {volume_change_percent:,.2f}
<b>Rank:</b> {rank}
<b>Total Supply:</b> {total_supply:,.0f}
<b>Circulating Supply:</b> {circulating_supply:,.0f}
<b>Market Cap:</b> ${market_cap:,.2f}
<b>ATH Value:</b> ${ath_value:,.8f}
<b>ATH Percent Change:</b> {token.ath_percent_change:,.2f}%
<b>ATL Value:</b> ${atl_value:,.8f}
<b>ATL Percent Change:</b> {token.atl_percent_change:,.2f}%
        '''
        bot = call.bot
        input_file=BufferedInputFile(chart_buf.read(),filename='chart.png')
        await tokens.update({'ticker':ticker,'user_id':user_id},{'rank':rank,'ath_value':ath_value,'atl_value':atl_value,'total_supply':total_supply,'circulating_supply':circulating_supply,'market_cap':market_cap})
        await bot.edit_message_media(media=InputMediaPhoto(media=input_file,caption=text),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=get_inline_back_kb(ticker=ticker),            
                                     )
        
      
        
    elif data=='back':
        client=BybitClient(config.api.bybit_url)
        try:
            ticker_from_api=await client.fetch_token_info(ticker)
        finally:
            await client.close()

        last_pump_price=token.last_price
        current_price=float(ticker_from_api['lastPrice'])
        price_change_in_percent = ((current_price - last_pump_price) / last_pump_price) * 100
        await call.message.edit_caption(caption=f'''
                                ByBit — {token.pump_period} — <b>{ticker}</b>
<b>Pump</b>: {price_change_in_percent:.2f}% ({last_pump_price} - {current_price})
<b>Signal 24</b>: {token.sygnal_per_day}
<b>Percent change in 24h</b>: {token.price_change:.2f}
                                ''',parse_mode='HTML',reply_markup=get_inline_kb(token))
    
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
    

    

    
        
  