from asyncio import create_task
import asyncio
from aiogram import Router,F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from database.repo.requests import RequestsRepo
from client_api.schemas import Token
from database.models import TokenForPump
from client_api.bybit_api import BybitClient
from services.pump_and_dump_screener import track_prices
screener_router=Router()







@screener_router.message(F.text=='/run')
async def run_screener(message:Message,config,state:FSMContext,user,repo:RequestsRepo):

    try:
        base_url=config.api.url
        bybit_client=BybitClient(base_url)
        tokens:list[Token]=await bybit_client.fetch_spot_symbols()
    except:
        print('connection error')
    finally:
        await bybit_client.close()

    pump_tokens_repo=repo.pump_tokens
    # dump_tokens_repo=repo.dump_tokens
    
    if await pump_tokens_repo.is_table_empty():
        try:
            base_url=config.api.url
            bybit_client=BybitClient(base_url)
            tokens:list[Token]=await bybit_client.fetch_spot_symbols()
        finally:
            await bybit_client.close()
        pump_tokens=[TokenForPump(ticker=token.ticker,last_price=token.last_price,sygnal_per_day=0) for token in tokens]
        # dump_tokens=[TokenForDump(ticker=token.ticker,last_price=token.last_price) for token in tokens]
        await pump_tokens_repo.add_all(pump_tokens)
        # await dump_tokens_repo.add_all(dump_tokens)

    settings_repo = repo.settings
    settings=await settings_repo.get_one_or_none(user_id=user.id)
    if settings is None:
        settings=await settings_repo.add(user_id=user.id,pump_period=15,dump_period=15,pump_percent=1,dump_percent=3)

    task=create_task(track_prices(message,repo,settings,config))
  
    
    await state.update_data(task=task)
    await message.answer(text='Скринер запущен')
    await asyncio.gather(task)
  
   
  

@screener_router.message(F.text=='/delete_database')
async def run_screener(message:Message,repo:RequestsRepo):
    pump_repo=repo.pump_tokens
    await pump_repo.delete_all()
    await message.answer('База данных очищена')




@screener_router.message(F.text=='/stop')
async def stop_screener(message:Message,state:FSMContext):
    data=await state.get_data()
    task=data.get('task',None)
  
    if task is not None:
            if task.done() is False:
                print('Cancelling')
                task.cancel()
                await asyncio.sleep(0.1)
                if task._state=='CANCELLED':
                    await message.answer('Скринер остановлен')
    else:
        await message.answer('Скринер уже остановлен')
                

              
               
        
       
        

    
