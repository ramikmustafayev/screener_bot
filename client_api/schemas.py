from dataclasses import dataclass


@dataclass
class Token:
    ticker:str
    last_price:float