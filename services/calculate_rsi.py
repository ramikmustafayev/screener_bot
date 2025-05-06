
         
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




def process_symbol_data(args):
    symbol=args['symbol']
    klines=args['list']

    if len(klines) < 15:
        return {"symbol": symbol, "rsi14": 0}

    closes = [float(kline[4]) for kline in klines][::-1]
    rsi_value = calculate_rsi(closes, period=14)



    return {
        "symbol": symbol,
        "rsi14": round(rsi_value, 2) if rsi_value is not None else None,
    
    }




