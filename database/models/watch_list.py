from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column,relationship
from sqlalchemy import Integer,ForeignKey
from sqlalchemy import ForeignKeyConstraint
from .base import Base

if TYPE_CHECKING:
    from .users import User



class WatchList(Base):
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    ticker:Mapped[str]
    target_price:Mapped[float]
    direction:Mapped[str]
    user_id:Mapped[int]=mapped_column(ForeignKey('users.id'))
    user:Mapped['User']=relationship('User',back_populates='watchlist')
