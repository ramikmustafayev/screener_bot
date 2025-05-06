from client_api.base import BaseClient
from client_api.schemas import Token
from services.rate_limiter import rate_limited

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
            if token['symbol'][-4:]=='USDT':
                tokens.append(Token(ticker=token['symbol'],last_price=float(token['lastPrice']),volume_per_day=float(token['turnover24h']),price_change=float(token['price24hPcnt'])))
      
        return tokens
    
    async def fetch_token_info(self,symbol):
        params={'category':'spot','symbol':symbol}
        result=await self.make_request(method='GET',url='/v5/market/tickers/',params=params)
        token=result['result']['list'][0]
        return token
    
    @rate_limited(max_calls=600, period=5)
    async def fetch_klines(self,symbol,interval='60',limit=100):
        params={
        'symbol':symbol,
        'category':'spot',
        'interval':interval,
        'limit':limit
    }
        try:
            result=await self.make_request(method='GET',url='/v5/market/kline/',params=params)
            return result['result']
            
        except Exception as e:
            print('Error fetching klines:', e)
            return None
        
    

    async def get_orderbook(self,symbol,limit=50):
        params={
            'symbol':symbol,
            'category':'spot',
            'limit':limit
        }
        
        try:
            result=await self.make_request(method='GET',url='/v5/market/orderbook/',params=params)
            return result['result']
        except Exception as e:
            print('Error by getting orderbook', e)
            return None
        

    