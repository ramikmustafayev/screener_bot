from client_api.base import BaseClient
from client_api.schemas import Token
class BybitClient(BaseClient):

    def __init__(self,base_url):
        super().__init__(base_url)
        self.base_url = base_url





    async def fetch_spot_symbols(self):
        
        tokens=[]
        params={'category':'spot'}
        result=await self.make_request(method='GET',url='/v5/market/tickers/',params=params)
        token_list=result['result']['list']
        for token in token_list:
            tokens.append(Token(ticker=token['symbol'],last_price=float(token['lastPrice'])))
      
        return tokens
    
    async def fetch_token_price(self,symbol):
        params={'category':'spot','symbol':symbol}
        result=await self.make_request(method='GET',url='/v5/market/tickers/',params=params)
        token=result['result']['list'][0]
        return float(token['lastPrice'])
    