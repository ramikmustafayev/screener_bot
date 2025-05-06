def calculate_sma50(args):
    symbol = args['symbol']
    klines = args['list']
    


    # Разворачиваем, чтобы старые были первыми
    klines = list(reversed(klines))
    
    # Берём последние 50 закрытых свечей
    klines = klines[-50:]
    close_prices = [float(kline[4]) for kline in klines]

    if len(close_prices) < 50:
        return {"symbol": symbol, "sma50": 0}

    # Вычисляем SMA
    sma50 = str(round(sum(close_prices) / len(close_prices), 6))
    return {
        "symbol": symbol,
        "sma50": sma50,
    }