import asyncio
from datetime import datetime,timedelta
from client_api.schemas import Token
from client_api.bybit_api import BybitClient
from database.repo.requests import RequestsRepo



async def track_prices(message,repo:RequestsRepo,settings,config):
            base_url=config.api.url
            bybit_client=BybitClient(base_url)
            try:
                while True:
                    try:
                        tokens:list[Token]=await bybit_client.fetch_spot_symbols()
                    except Exception as e:
                        await bybit_client.close()

                    pump_period=settings.pump_period
                    pump_percent=settings.pump_percent
                    # dump_period=settings.dump_period
                    # dump_percent=settings.dump_percent
                
                    current_time=datetime.now()

                    for token in tokens:

                        ticker_name=token.ticker
                             
                        current_price=token.last_price
                        pump_token_from_db=await repo.pump_tokens.get_one_or_none(ticker=ticker_name)
                        # dump_token_from_db=await repo.dump_tokens.get_one_or_none(ticker=ticker_name)
                        
                       
                        if pump_token_from_db is None:
                            new_pump_token= await repo.pump_tokens.add(ticker=token.ticker,last_price=token.last_price,sygnal_per_day=0)
                            # new_dump_token= await repo.dump_tokens.add(ticker=token.ticker,last_price=token.last_price)
                            pump_token_from_db=new_pump_token
                            # dump_token_from_db=new_dump_token
                            
                        
                        last_pump_price=pump_token_from_db.last_price
                        last_pump_update=pump_token_from_db.updated_at
                        sygnal_per_day=pump_token_from_db.sygnal_per_day

                        # last_dump_price=dump_token_from_db.last_price
                        # last_dump_update=dump_token_from_db.updated_at

                        print(current_time-last_pump_update)
                        if current_time-last_pump_update<timedelta(minutes=pump_period):
                            price_change_in_percent = ((current_price - last_pump_price) / last_pump_price) * 100
                            if price_change_in_percent>=pump_percent:
                                sygnal_per_day+=1
                                await repo.pump_tokens.update({'ticker':ticker_name},{'last_price':current_price,'sygnal_per_day':sygnal_per_day})
                                href='https://www.coinglass.com/tv/Bybit_'+ticker_name
                                await message.answer(f'''
                                ByBit — {pump_period} — <a href="{href}">{ticker_name}</a>
<b>Pump</b>: {price_change_in_percent:.2f}% ({last_pump_price} - {current_price})
<b>Signal 24</b>: {sygnal_per_day}
                                ''',parse_mode='HTML')
                        else:
                            await repo.pump_tokens.update({'ticker':ticker_name},{'updated_at':current_time})
                    

#                         if current_time-last_dump_update<timedelta(minutes=dump_period):
#                             price_change_in_percent = ((current_price - last_dump_price) / last_dump_price) * 100
#                             if price_change_in_percent<=-dump_percent:
#                                 href='https://www.coinglass.com/tv/Bybit_'+ticker_name
#                                 await repo.dump_tokens.update({'ticker':ticker_name},{'last_price':current_price})
#                                 await message.answer(f'''
#                                 ByBit — {dump_period} — <a href="{href}">{ticker_name}</a>
# <b>Dump</b>: {price_change_in_percent:.2f}% ({last_dump_price} - {current_price})
#                                 ''',parse_mode='HTML')
#                         else:
#                             await repo.dump_tokens.update({'ticker':ticker_name},{'updated_at':current_time})

                   
                   
                    await asyncio.sleep(2)
                            
            except asyncio.CancelledError as e:
                await bybit_client.close()
                raise asyncio.CancelledError
            



