from sqlalchemy.orm import Mapped, mapped_column,relationship
from sqlalchemy import ForeignKey,Integer
from .base import Base
# from .users import User


class Settings(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    pump_period:Mapped[int]
    pump_percent:Mapped[float]
    dump_period:Mapped[int]
    dump_percent:Mapped[float]
    user = relationship('User', back_populates='settings')
     
     