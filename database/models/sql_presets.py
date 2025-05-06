import typing
from sqlalchemy.orm import Mapped, mapped_column,relationship
from sqlalchemy import ForeignKey,String,Integer,Text
from sqlalchemy.ext.hybrid import hybrid_property
from .base import Base

if typing.TYPE_CHECKING:
    from .users import User


class SQLPreset(Base):


    id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id:Mapped[int]=mapped_column(ForeignKey('users.id'))
    name:Mapped[str] = mapped_column(String, unique=True, nullable=False)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    user:Mapped['User']=relationship('User',back_populates='sqlpresets')