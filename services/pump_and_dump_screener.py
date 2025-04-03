import asyncio
from datetime import datetime,timedelta
from database.models.tokens import Token
from database.models.users import User
from database.repo.requests import RequestsRepo
from keyboards.all_keyboards import get_inline_kb
from client_api.bybit_api import BybitClient
from client_api.schemas import Token as TokenSchema


async def track_prices(message,repo:RequestsRepo,user:User,config):
            base_url=config.api.bybit_url
            bybit_client=BybitClient(base_url)
            try:
                while True:
                    try:
                        tokens:list[TokenSchema]=await bybit_client.fetch_spot_symbols()
                    except Exception as e:
                        await bybit_client.close()
                    finally:
                        await bybit_client.close()

                  
                
                    current_time=datetime.now()

                    for token in tokens:

                        ticker_name=token.ticker
                        current_price=token.last_price
                        
                        

                        token_from_db:Token=await repo.tokens.get_one_or_none(ticker=ticker_name)

                        if token_from_db.is_in_blacklist:
                            continue

                
                        is_interesting=token_from_db.is_interesting 
                        pump_period=token_from_db.pump_period
                        pump_percent=token_from_db.pump_percent
                        last_pump_price=token_from_db.last_price
                        last_pump_update=token_from_db.updated_at
                        sygnal_per_day=token_from_db.sygnal_per_day
                        
                        
                        if current_time-last_pump_update<timedelta(minutes=pump_period):
                            
                            price_change_in_percent = ((current_price - last_pump_price) / last_pump_price) * 100
                
                            if price_change_in_percent>=pump_percent:
                                sygnal_per_day+=1
                                await repo.tokens.update({'ticker':ticker_name},{'last_price':current_price,'sygnal_per_day':sygnal_per_day,'updated_at':current_time})
                                await message.answer(f'''
                                ByBit — {pump_period} — <b>{ticker_name}</b>
<b>Pump</b>: {price_change_in_percent:.2f}% ({last_pump_price:.8f} - {current_price:.8f})
<b>Signal 24</b>: {sygnal_per_day}
                                ''',parse_mode='HTML',reply_markup=get_inline_kb(ticker_name,is_interesting=is_interesting))
                        else:
                            await repo.tokens.update({'ticker':ticker_name,'user_id':user.id},{'last_price':current_price,'updated_at':current_time})
                    
                    await asyncio.sleep(1)
                            
            except asyncio.CancelledError as e:
                raise asyncio.CancelledError
            



