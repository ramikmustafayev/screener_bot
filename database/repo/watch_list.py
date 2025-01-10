from database.repo.base import BaseRepo
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from database.models import WatchList
class WatchListRepo(BaseRepo):
    model=WatchList

    async def get_all_by_user_id(self,user_id):
        stmt=select(self.model).filter_by(user_id=user_id)
        try:
            results= await self.session.scalars(stmt)
        except SQLAlchemyError:
            raise
        
        return results.all()
    
    


        


    