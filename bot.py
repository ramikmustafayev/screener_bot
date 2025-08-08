import asyncio
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot,Dispatcher
from sqlalchemy.ext.asyncio import AsyncSession
from config import load_config,Config
from middlewares.config import ConfigMiddleware
from middlewares.database import DatabaseMiddleware
from handlers import routers_list
from database.setup import create_engine,create_session_pool



async def set_commands(bot):
    commands = [BotCommand(command='start', description='Запуск бота'),
                BotCommand(command='run_screener', description='Запустить скринер'),
                BotCommand(command='stop_screener', description='Остановить скринер'),
                BotCommand(command='add_to_watchlist', description='Добавить монету в список отслеживаемых токенов'),
                BotCommand(command='delete_from_watchlist', description='Удалить монету из списка отслеживаемых токенов'),
                BotCommand(command='watchlist', description='Показать список отслеживаемых токенов'),
                BotCommand(command='token_info', description='Показать информацию о токене'),
                BotCommand(command='refresh_database', description='Обновить базу данных'),
                BotCommand(command='update_token_info', description='Обновить базу данных с CryptoRank'),
                BotCommand(command='add_preset', description='Добавить новый пресет с запросом SQL'),
                BotCommand(command='delete_preset', description='Удалить пресет по ID'),
                BotCommand(command='list_presets', description='Показать список пресетов'),
                BotCommand(command='get_preset', description='Получить запрос для выбранного пресета по ID'),
                BotCommand(command='run_preset', description='Выполнить пресет с заданным ID'),
                ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
    

def register_global_middlewares(dp:Dispatcher,config:Config,session_pool:AsyncSession):
    middleware_types=[
     ConfigMiddleware(config),
     DatabaseMiddleware(session_pool),
    ]

    for middleware_type in middleware_types:
        dp.update.outer_middleware(middleware_type)

  


async def main():
    config:Config=load_config()
    engine=create_engine(config.db)
    session_pool=create_session_pool(engine)
    bot=Bot(token=config.tg_bot.token,default=DefaultBotProperties(parse_mode='HTML'))
    await bot.delete_webhook(drop_pending_updates=True)
    dp=Dispatcher(storage=MemoryStorage())
    dp.include_routers(*routers_list)
    register_global_middlewares(dp,config,session_pool)
    await set_commands(bot)
    await dp.start_polling(bot)




if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot is disabled')