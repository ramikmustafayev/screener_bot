from sqlalchemy import update,select
from database.repo.base import BaseRepo
from database.models.settings import Settings


class SettingsRepo(BaseRepo):
    model = Settings


    async def get_or_create(self,user_id:int):
        settings=await self.get_one_or_none(user_id=user_id)
        if settings is None:
            settings=await self.add(user_id=user_id,pump_period=15,dump_period=15,pump_percent=1,dump_percent=3)
        return settings


    
    


    
