import aiohttp


# Функция для получения исторических данных по свечам
async def get_klines(symbol, interval="240", limit=50):
    url = "https://api.bybit.com/v5/market/kline"
    params = {
        "category": "spot",
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            data = await response.json()
    
    if data["retCode"] == 0:
        return data["result"]["list"]
    else:
        raise Exception(f"Ошибка API: {data}")

# Функция для вычисления SMA 50
async def calculate_sma50(symbol):
    klines = await get_klines(symbol)

    # Достаем последние 50 закрытых цен
    close_prices = [float(kline[4]) for kline in klines]

    # Вычисляем среднее
    sma50 =str(round(sum(close_prices) / len(close_prices),2))
    return sma50


