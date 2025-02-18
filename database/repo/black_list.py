from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from database.repo.base import BaseRepo
from database.models.black_list import BlackList



class BlackListRepo(BaseRepo):
    model = BlackList




    async def get_all(self):
        stmt=select(self.model)
        try:
            results= await self.session.scalars(stmt)
        except SQLAlchemyError:
            raise
        
        return results.all()



