import aiohttp
import asyncio
from datetime import datetime

async def fetch_klines(session, symbol="BTCUSDT", interval="240", limit=100):
    url = "https://api.bybit.com/v5/market/kline"
    params = {
        "category": "spot",
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    async with session.get(url, params=params) as response:
        data = await response.json()
        if data["retCode"] == 0:
            return data["result"]["list"]
        else:
            raise Exception(f"API Error: {data['retMsg']}")

def calculate_rsi(prices, period=14):
    prices = [float(price) for price in prices]
    if len(prices) < period + 1:  # Нужно минимум period+1 свечей для period изменений
        return None
    
    # Вычисляем изменения цен
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    
    # Начальные средние для первых period изменений
    gains = [delta for delta in deltas[:period] if delta > 0] or [0]
    losses = [-delta for delta in deltas[:period] if delta < 0] or [0]
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    
    # Последовательное сглаживание для оставшихся значений
    for delta in deltas[period:]:
        gain = delta if delta > 0 else 0
        loss = -delta if delta < 0 else 0
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
    
    # Вычисляем RSI
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

async def get_rsi14(symbol="BTCUSDT"):
    async with aiohttp.ClientSession() as session:
        klines = await fetch_klines(session, symbol, "240", 100)
        
        # Переворачиваем порядок: от старых к новым
        closes = [kline[4] for kline in klines][::-1]
        
        # Берем все доступные данные (минимум 15 свечей для RSI14)
        rsi_value = calculate_rsi(closes, period=14)
        
        last_timestamp = datetime.fromtimestamp(int(klines[0][0]) / 1000)
        
        return {
          
            "rsi14": round(rsi_value, 2) if rsi_value is not None else None,
           
        }

