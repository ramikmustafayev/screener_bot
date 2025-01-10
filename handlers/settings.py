from aiogram import Router ,F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from keyboards.all_keyboards import create_settings_kb,create_cancel_keyboard
from states.states import  PumpState,DumpState
from database.repo.requests import RequestsRepo
from database.models.users import User
from aiogram.types import ReplyKeyboardRemove
settings_router=Router()


@settings_router.message(F.text=='/settings')
async def cmd_settings(message:Message):
    await message.answer(f'Я сканирую рынок на маленькие пампы и резкие просадки. ',reply_markup=create_settings_kb())


@settings_router.message(F.text=='Период пампа')
async def cmd_settings(message:Message,state:FSMContext,user:User,repo:RequestsRepo):
    await state.set_state(PumpState.pump_period)
    settings=await repo.settings.get_or_create(user_id=user.id)
    await message.answer(f'Текущий период времени, за который должен произойти памп - {settings.pump_period} мин. Введите новый период времени: От 1 до 30 мин',reply_markup=create_cancel_keyboard())

@settings_router.message(F.text=='Процент пампа')
async def cmd_settings(message:Message,state:FSMContext,user:User,repo:RequestsRepo):
    await state.set_state(PumpState.pump_percent)
    settings=await repo.settings.get_or_create(user_id=user.id)
    await message.answer(f'Текущий % изменения цены для пампа - {settings.pump_percent} %. Введите новый % изменения цены для пампа',reply_markup=create_cancel_keyboard())

@settings_router.message(F.text=='Период дампа')
async def cmd_settings(message:Message,state:FSMContext,user:User,repo:RequestsRepo):
    settings=await repo.settings.get_or_create(user_id=user.id)
    await state.set_state(DumpState.dump_period)
    await message.answer(f'Текущий период времени, за который должен произойти дамп - {settings.dump_period} мин. Введите новый период времени: От 1 до 30 мин',reply_markup=create_cancel_keyboard())
@settings_router.message(F.text=='Процент дампа')
async def cmd_settings(message:Message,state:FSMContext,user:User,repo:RequestsRepo):
    settings=await repo.settings.get_or_create(user_id=user.id)
    await state.set_state(DumpState.dump_percent)
    await message.answer(f'Текущий % изменения цены для дампа - {settings.dump_percent} %. Введите новый % изменения цены для пампа',reply_markup=create_cancel_keyboard())



@settings_router.message(F.text=='Отмена')
async def cancel(message:Message,state:FSMContext):
    await message.answer('Отмена',reply_markup=ReplyKeyboardRemove())
    await state.set_state(None)
    

@settings_router.message(PumpState.pump_period)
async def process_pump_period(message:Message,state:FSMContext,user:User,repo:RequestsRepo):
    data=message.text
    await update_data(user,{'pump_period':int(data)},repo)
        
    await message.answer(f'new value for pump period {data}',reply_markup=ReplyKeyboardRemove())
    await state.set_state(None)

@settings_router.message(PumpState.pump_percent)
async def process_pump_percent(message:Message,state:FSMContext,user,repo:RequestsRepo):
    data=message.text
    await update_data(user,{'pump_percent':float(data)},repo)
    await message.answer(f'new value for pump percent {float(data)}')
    await state.set_state(None)


@settings_router.message(DumpState.dump_period)
async def process_dump_period(message:Message,state:FSMContext,user,repo:RequestsRepo):
    data=message.text
    await update_data(user,{'dump_period':int(data)},repo)
    await message.answer(f'new value for dump period {int(data)}')
    await state.set_state(None)


@settings_router.message(DumpState.dump_percent)
async def process_pump_percent(message:Message,state:FSMContext,user,repo:RequestsRepo):
    data=message.text
    await update_data(user,{'dump_percent':float(data)},repo)
    await message.answer(f'new value for dump percent {float(data)}')
    await state.set_state(None)



async def update_data(user,values_dict,repo:RequestsRepo):
    settings_repo=repo.settings
    await settings_repo.update({'user_id':user.id}, values_dict)