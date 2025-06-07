import pandas as pd

def calculate_ema(args):

    symbol = args['symbol']
    klines = args['list']

    if len(klines) < 8:
        return {"symbol": symbol, "ema": 0, "last_price": 0}

    df = pd.DataFrame(klines, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'Turnover'])
    df['Close'] = df['Close'].astype(float)
    df = df.sort_values(by='timestamp')

    df['EMA'] = df['Close'].ewm(span=7, adjust=False).mean()
    last_ema = df['EMA'].iloc[-1]
    last_price = df['Close'].iloc[-1]

    return {
        'symbol': symbol,
        'ema': last_ema,
        'last_price': last_price
    }
