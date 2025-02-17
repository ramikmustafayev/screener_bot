from sqlalchemy.orm import Mapped, mapped_column,relationship
from sqlalchemy import ForeignKey,Integer
from .base import Base
from .users import User


class TokenBase(Base):
     __abstract__ = True

     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
     ticker:Mapped[str]
     last_price:Mapped[float]
     sygnal_per_day:Mapped[int]



class TokenForPump(TokenBase):
     pass


class TokenForDump(TokenBase):
     pass







