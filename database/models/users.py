from sqlalchemy.orm import Mapped, mapped_column,relationship
from sqlalchemy import BigInteger
from .base import Base
from .watch_list import WatchList
from .settings import Settings

class User(Base):
    id:Mapped[int]=mapped_column(BigInteger,primary_key=True)
    name:Mapped[str]
    watchlist:Mapped[list['WatchList']]=relationship('WatchList',back_populates='user',cascade='all,delete-orphan')
    settings = relationship('Settings', back_populates='user', uselist=False)