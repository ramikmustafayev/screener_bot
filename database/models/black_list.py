from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer
from .base import Base



class BlackList(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticker: Mapped[str]