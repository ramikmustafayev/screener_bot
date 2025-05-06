def calculate_volume_changes(args):
    symbol=args['symbol']
    klines=args['list']

    if len(klines) < 2:
        return {"symbol": symbol, "percent": 0}
    
    # Достаем последние 50 закрытых цен
    today = float(klines[0][5])      # объем сегодняшнего дня
    yesterday = float(klines[1][5])  # объем вчерашнего дня

    change_percent = ((today - yesterday) / yesterday) * 100
    return {
        "symbol": symbol,
        "percent": change_percent,
    }