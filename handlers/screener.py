from asyncio import create_task
import asyncio
from aiogram import Router,F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from database.repo.requests import RequestsRepo
from services.pump_and_dump_screener import track_prices
from services.populate_database import populate_database
from services.update_database import update_database
screener_router=Router()







@screener_router.message(F.text=='/run')
async def run_screener(message:Message,config,state:FSMContext,user,repo:RequestsRepo):

    first=False
    tokens_repo=repo.tokens
    
    if await tokens_repo.is_table_empty():
        first=True
        await populate_database(config,tokens_repo,user)

    if not first:
        await update_database(config,tokens_repo,user)


    task=create_task(track_prices(message,repo,user,config))
  
    
    await state.update_data(task=task)
    await message.answer(text='Скринер запущен')
    await asyncio.gather(task)
  
   
  






@screener_router.message(F.text=='/stop')
async def stop_screener(message:Message,state:FSMContext):
    data=await state.get_data()
    task=data.get('task',None)
  
    if task is not None:
            if task.done() is False:
                print('Cancelling')
                task.cancel()
                await asyncio.sleep(0.5)
                if task._state=='CANCELLED':
                    await message.answer('Скринер остановлен')
    else:
        await message.answer('Скринер уже остановлен')
                

              
               
        
       
        

    
