from datetime import datetime
from sqlalchemy.orm import DeclarativeBase,declared_attr,Mapped,mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs





class Base(AsyncAttrs,DeclarativeBase):
    __abstract__=True
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now())
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(), onupdate=lambda: datetime.now())
    

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'
    