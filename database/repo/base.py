from sqlalchemy import select,update,delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import asc

class BaseRepo:
    model=None

    def __init__(self,session):
        self.session = session



    async def add_all(self,tokens):
        self.session.add_all(tokens)
        try:
            await self.session.commit()
        except SQLAlchemyError:
            await self.session.rollback()
            raise

    
    async def add(self,**values):
        token=self.model(**values)
        self.session.add(token)
        try:
            await self.session.commit()
            await self.session.refresh(token)
        except SQLAlchemyError:
            await self.session.rollback()
            raise

        return token
    


    async def get_one_or_none(self,**filter):
        try:
            stmt=select(self.model).filter_by(**filter)
            token=await self.session.scalar(stmt)
        except SQLAlchemyError:
            raise
        return token
    
    async def get_all(self, order_by=None,offset=None, limit=None, **filter):
        try:
            stmt = select(self.model).filter_by(**filter)
            if order_by:
                stmt = stmt.order_by(asc(order_by))
            if offset:
                stmt = stmt.offset(offset)
            if limit:
                stmt = stmt.limit(limit)
            result = await self.session.scalars(stmt)
            tokens= result.all()
            for token in tokens:
                await self.session.refresh(token)  # Принудительно обновляем каждый объект
            return tokens
        except SQLAlchemyError:
            raise



    async def is_table_empty(self,**filter):
        stmt=select(self.model.id).filter_by(**filter).limit(1)
        result=await self.session.scalar(stmt)
        return result is None
    


    async def update(self,filter_dict,values_dict):
        
        stmt=update(self.model).where(*[getattr(self.model,k)==v for k,v in filter_dict.items()]).values(**values_dict).execution_options(synchronize_session='fetch')
        try:
            await self.session.execute(stmt)
            await self.session.commit()
            stmt_select = select(self.model).filter_by(**filter_dict)
            updated_object = await self.session.scalar(stmt_select)
            return updated_object
        except SQLAlchemyError:
            await self.session.rollback()


    
    async def delete(self,filter):
        stmt=delete(self.model).filter_by(**filter)
        try:
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount
        except SQLAlchemyError:
            await self.session.rollback()


    async def delete_all(self):
        stmt=delete(self.model)
        try:
            await self.session.execute(stmt)
            await self.session.commit()
        except SQLAlchemyError:
            await self.session.rollback()



    