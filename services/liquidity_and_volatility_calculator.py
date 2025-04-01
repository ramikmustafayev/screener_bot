import aiohttp
import math


async def get_historical_data(symbol,interval='60',limit=100):
    url='https://api.bybit.com/v5/market/kline'
    params={
        'symbol':symbol,
        'category':'spot',
        'interval':interval,
        'limit':limit
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url,params=params) as response:
            data=await response.json()
            if data['retCode']==0:
                return [float(candle[4]) for candle in data['result']['list']]
            else:
                print('error')
                return None
            

async def calculate_volatility(symbol,interval='60',limit=100):
    prices=await get_historical_data(symbol,interval,limit)
 
    if prices is None or len(prices)<2:
        return None
    
    returns=[(prices[i]-prices[i-1])/prices[i-1]*100 for i in range(1,len(prices))]
    mean_return=sum(returns)/len(returns)

    variance=sum((r-mean_return) ** 2 for r in returns)/len(returns)
    volatility=math.sqrt(variance)
    # annualized_volatility=volatility*math.sqrt(365*(24/int(interval)))

    return round(volatility,4)



    

async def get_orderbook(symbol):
    url='https://api.bybit.com/v5/market/orderbook'
    params={
        'symbol':symbol,
        'category':'spot',
        'limit':'50'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url,params=params) as response:
            data=await response.json()
            if data['retCode']==0:
                return data['result']
            else:
                print('error')
                return None
            

async def calculate_liquidity(symbol):
    orderbook=await get_orderbook(symbol)
    if orderbook is None:
        return None
    

    bids=[(float(price),float(size)) for price,size in orderbook['b']]
    asks=[(float(price),float(size)) for price,size in orderbook['a']]
    
    best_bid=bids[0][0]
    best_ask=asks[0][0]
    mid_price=(best_bid+best_ask)/2
    spread=((best_ask-best_bid)/mid_price)*100

    def get_depth(order_list,direction):
        depth=0
        for price,size in order_list:
            if direction=='buy' and price>=mid_price*0.99:
                depth+=size*price
            elif direction=='sell' and price<=mid_price*1.01:
                depth+=size*price
            else:
                break
        return depth
    

    buy_liq=get_depth(bids,'buy')
    sell_liq=get_depth(asks,'sell')
    total_liq=buy_liq+sell_liq

    return {'spread(%)':round(spread,4),'buy_liq(1%)':round(buy_liq,2),'sell_liq(1%)':round(sell_liq,2),'total_liq':round(total_liq,2)}