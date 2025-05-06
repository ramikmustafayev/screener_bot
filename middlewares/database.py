from typing import Callable, Dict, Any, Awaitable,Union

from aiogram import BaseMiddleware
from aiogram.types import Message,Update,CallbackQuery,Message,TelegramObject

from database.repo.requests import RequestsRepo



class DatabaseMiddleware(BaseMiddleware):
    def __init__(self,session_pool)->None:
        self.session_pool = session_pool

    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        
        user=data['event_from_user']

        
       
        


        async with self.session_pool() as session:
            repo=RequestsRepo(session)

            user=await repo.users.get_or_create_user(
                user.id,
                user.full_name
            )

            data['session']=session
            data['repo']=repo
            data['user']=user

            result=await handler(event, data)

        return result
            