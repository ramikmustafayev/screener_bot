import typing
from sqlalchemy.orm import Mapped, mapped_column,relationship
from sqlalchemy import ForeignKey,Integer
from .base import Base

if typing.TYPE_CHECKING:
    from .users import User



class Token(Base):
   
     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
     ticker:Mapped[str]
     last_price:Mapped[float]
     sygnal_per_day:Mapped[int]
     pump_percent:Mapped[float]
     pump_period:Mapped[int]
     is_in_blacklist:Mapped[bool]
     is_interesting:Mapped[bool]
     user_id:Mapped[int]=mapped_column(ForeignKey('users.id'))
     user:Mapped['User']=relationship('User',back_populates='tokens')











