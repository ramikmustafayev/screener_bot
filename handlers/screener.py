from asyncio import create_task
import asyncio
from aiogram import Router,F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from database.repo.requests import RequestsRepo
from aiogram.utils.chat_action import ChatActionSender
from services.pump_and_dump_screener import track_prices
from services.update_database import update_database
from client_api.bybit_api import BybitClient
screener_router=Router()







@screener_router.message(F.text=='/run_screener')
async def run_screener(message:Message,config,state:FSMContext,user,repo:RequestsRepo):
    data=await state.get_data()
    task=data.get('task',None)
  
    if task is not None:
        await message.answer('Скринер уже запущен')
        return None

    
    msg = await message.answer(text='Скринер запускается...')
    tokens_repo=repo.tokens
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        try:
            bybit_client=BybitClient(config.api.bybit_url)
            await update_database(bybit_client,tokens_repo,user)  # Имитация долгой операции
            await msg.edit_text("Скринер запущен ✅")
        except Exception as e:
            print('Error:', e)
            await msg.edit_text("Произошла ошибка при запуске скринера ❌")
            return
        finally:
            await bybit_client.close()


    

    task=create_task(track_prices(message,repo,user,config))
  

    await state.update_data(task=task)
    await asyncio.gather(task)
  
   
  






@screener_router.message(F.text=='/stop_screener')
async def stop_screener(message:Message,state:FSMContext):
    data=await state.get_data()
    task=data.get('task',None)
  
    if task is not None:
            if task.done() is False:
                task.cancel()
                await asyncio.sleep(0.5)
                if task._state=='CANCELLED':
                    await message.answer('Скринер остановлен')
                    await state.update_data(task=None)
    else:
        await message.answer('Скринер уже остановлен')
                

              
               
        
       
        

    
