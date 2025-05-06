from dataclasses import dataclass


@dataclass
class Token:
    ticker:str=None
    last_price:float=0.0
    rank:int=0
    total_supply:int=0
    circulating_supply:int=0
    ath_value:float=0.0
    atl_value:float=0.0
    price_change:float=0.0
    volume_per_day:float=0.0
