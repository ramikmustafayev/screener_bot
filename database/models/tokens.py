import typing
from sqlalchemy.orm import Mapped, mapped_column,relationship
from sqlalchemy import ForeignKey,Integer,Boolean
from sqlalchemy.ext.hybrid import hybrid_property
from .base import Base

if typing.TYPE_CHECKING:
    from .users import User



class Token(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticker:Mapped[str]
    rank: Mapped[int] = mapped_column(Integer, default=0)
    last_price:Mapped[float]
    total_supply: Mapped[int] = mapped_column(default=0)
    circulating_supply: Mapped[int] = mapped_column(default=0)
    ath_value: Mapped[float] = mapped_column(default=0.0)
    atl_value:Mapped[float] = mapped_column(default=0.0)
    sygnal_per_day:Mapped[int]
    pump_percent:Mapped[float]
    pump_period:Mapped[int]
    is_in_blacklist:Mapped[bool]
    is_muted:Mapped[bool]=mapped_column(default=False)
    user_id:Mapped[int]=mapped_column(ForeignKey('users.id'))
    user:Mapped['User']=relationship('User',back_populates='tokens')
    price_change:Mapped[float]=mapped_column(default=0.0)
    sma:Mapped[float]=mapped_column(default=0.0)
    ema:Mapped[float]=mapped_column(default=0.0)
    rsi:Mapped[float]=mapped_column(default=0.0)
    volume_per_day:Mapped[float]=mapped_column(default=0.0)
    volume_change:Mapped[float]=mapped_column(default=0.0)
    
    @hybrid_property
    def market_cap(self) -> float:
        return self.last_price * self.circulating_supply

    @market_cap.expression
    def market_cap(cls):
        return cls.last_price * cls.circulating_supply


    @hybrid_property
    def ath_percent_change(self) -> float:
        if self.ath_value == 0:
            return 0
        return (self.last_price - self.ath_value) / self.ath_value * 100

    @ath_percent_change.expression
    def ath_percent_change(cls):
        return ((cls.last_price - cls.ath_value) / cls.ath_value) * 100

    @hybrid_property
    def atl_percent_change(self) -> float:
        if self.atl_value == 0:
            return 0
        return (self.last_price - self.atl_value) / self.atl_value * 100

    @atl_percent_change.expression
    def atl_percent_change(cls):
        return ((cls.last_price - cls.atl_value) / cls.atl_value) * 100
    

    def __str__(self):
        return self.ticker
    
    def __repr__(self):
        return f"Token(ticker={self.ticker}, last_price={self.last_price}, rank={self.rank})"













