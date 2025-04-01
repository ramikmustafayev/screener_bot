import asyncio
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand, BotCommandScopeDefault
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot,Dispatcher
from sqlalchemy.ext.asyncio import AsyncSession
from config import load_config,Config
from middlewares.config import ConfigMiddleware
from middlewares.database import DatabaseMiddleware
from handlers import routers_list
from database.setup import create_engine,create_session_pool
from tasks.reset_column import reset_column



async def set_commands(bot):
    commands = [BotCommand(command='start', description='Запуск бота'),
                BotCommand(command='run', description='Запустить скринер'),
                BotCommand(command='stop', description='Остановить скринер'),
                BotCommand(command='add', description='Добавить монету в список отслеживаемых токенов'),
                BotCommand(command='delete', description='Удалить монету из списка отслеживаемых токенов'),
                BotCommand(command='list', description='Показать список отслеживаемых токенов'),
                BotCommand(command='token_info', description='Показать информацию о токене'),
                BotCommand(command='tokens_in_black_list', description='Показать токены в черном списке'),
                ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
    

def register_global_middlewares(dp:Dispatcher,config:Config,session_pool:AsyncSession):
    middleware_types=[
     ConfigMiddleware(config),
     DatabaseMiddleware(session_pool),
    ]

    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)

    for middleware_type in middleware_types:
        dp.callback_query.outer_middleware(middleware_type)
        



async def main():
    scheduler = AsyncIOScheduler()
    config:Config=load_config()
    engine=create_engine(config.db)
    session_pool=create_session_pool(engine)
    scheduler.add_job(reset_column, trigger=IntervalTrigger(days=1),args=[session_pool])
    bot=Bot(token=config.tg_bot.token,default=DefaultBotProperties(parse_mode='HTML'))
    await bot.delete_webhook(drop_pending_updates=True)
    dp=Dispatcher(storage=MemoryStorage())
    dp.include_routers(*routers_list)
    register_global_middlewares(dp,config,session_pool)
    await set_commands(bot)
    scheduler.start()
    await dp.start_polling(bot)




if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot is disabled')