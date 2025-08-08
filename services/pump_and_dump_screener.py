import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timedelta
from database.models.tokens import Token
from database.models.users import User
from database.repo.requests import RequestsRepo
from keyboards.all_keyboards import get_inline_kb
from client_api.bybit_api import BybitClient
import pandas as pd

length_high=4
length_low=4
swing_high_source = 'high'
swing_low_source = 'low'

def get_source_value(df, i, source):
    h, l, o, c = df['high'].iloc[i], df['low'].iloc[i], df['open'].iloc[i], df['close'].iloc[i]
    if source == 'high':
        return h
    elif source == 'low':
        return l
    elif source == 'open':
        return o
    elif source == 'close':
        return c
    elif source == '(h+l)/2':
        return (h + l) / 2
    elif source == '(h+l+c)/3':
        return (h + l + c) / 3
    elif source == '(h+l+c+o)/4':
        return (h + l + c + o) / 4
    elif source == '(h+l+c+c)/4':
        return (h + l + c + c) / 4
    else:
        raise ValueError(f"Неизвестный источник: {source}")

# Функция для поиска Swing High
def is_pivot_high(df, i, length, source):
    if i < length or i >= len(df) - length:
        return False
    current_value = get_source_value(df, i, source)
    for j in range(i - length, i + length + 1):
        if j != i and get_source_value(df, j, source) > current_value:
            return False
    return True

# Функция для поиска Swing Low
def is_pivot_low(df, i, length, source):
    if i < length or i >= len(df) - length:
        return False
    current_value = get_source_value(df, i, source)
    for j in range(i - length, i + length + 1):
        if j != i and get_source_value(df, j, source) < current_value:
            return False
    return True


def process_symbol(args):
    symbol = args['symbol']
    klines = args['list']

    if len(klines) < 8:
        return None

    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'])
    df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='ms')
    df = df.astype({'open': float, 'high': float, 'low': float, 'close': float, 'volume': float, 'turnover': float})
    df = df.iloc[::-1]  # Инвертируем порядок от старых к новым
    df.set_index('timestamp', inplace=True)

 
    swing_highs = []
    swing_lows = []
    for i in range(max(length_high, length_low), len(df) - max(length_high, length_low)):
            if is_pivot_high(df, i, length_high, swing_high_source):
                swing_highs.append((df.index[i], get_source_value(df, i, swing_high_source), i))
            if is_pivot_low(df, i, length_low, swing_low_source):
                swing_lows.append((df.index[i], get_source_value(df, i, swing_low_source), i))
        
        # Берем последний Swing High и Swing Low
    last_swing_high = swing_highs[-1] if swing_highs else None
    last_swing_low = swing_lows[-1] if swing_lows else None
        
        # Текущая цена (close последней свечи)
    current_price = df['close'].iloc[-1] if not df.empty else None
        
        # Проверяем, что текущая цена ниже или равна Swing High и разница не превышает 5% снижения
    
    if last_swing_high:
        return {    'date':last_swing_high[0],
                    'symbol': symbol,
                    'last_swing_high': last_swing_high,
                    'last_swing_low': last_swing_low,
                    'current_price': current_price,
                }
    
    
    return None



async def track_prices(message,repo:RequestsRepo,user:User,config):
    base_url = config.api.bybit_url
    bybit_client = BybitClient(base_url)
    token_repo = repo.tokens

 

    async def safe_fetch_klines(token:Token):
        try:
            return await bybit_client.fetch_klines(token.ticker, token.timeframe, 240)
        except Exception as e:
            print(f"Ошибка при получении данных для {token.ticker}: {e}")
            return None  # Возвращаем None для исключённых токенов

    try:
        while True:
            
            tokens = await token_repo.get_all(is_in_blacklist=False)
            active_tokens = []
            
            for token in tokens:
                if token.is_muted and datetime.now()- token.updated_at >=timedelta(minutes=15):
                    await token_repo.update({'ticker':token.ticker,'user_id':user.id},{'is_muted':False})
                if not token.is_muted:
                    active_tokens.append(token)

            
            # безопасный сбор данных
            tasks = [safe_fetch_klines(token) for token in active_tokens]
            results = await asyncio.gather(*tasks)

            results=[r for r in results if r]
            with ThreadPoolExecutor(max_workers=min(len(results), 4)) as executor:
                token_ema_list = list(executor.map(process_symbol, results))

           
            for token_data in token_ema_list:
                if not token_data:
                    await message.answer(f'Недостаточно данных по символу <b>{symbol}</b>')
                    continue
                print(token_data)
                last_swing_high = token_data.get('last_swing_high')[1]
                current_price = token_data.get('current_price')
                date= token_data.get('date')
                symbol = token_data.get('symbol')
                
                token:Token=await token_repo.get_one_or_none(ticker=symbol,user_id=user.id)
                if last_swing_high <= current_price <= last_swing_high * (1 + token.percent_change_ema / 100):
      
                    market_cap=token.circulating_supply*current_price
                    percent_drop = round((last_swing_high - current_price) / last_swing_high * 100, 2)
                    await message.answer(f'''<b>Symbol: </b> {symbol}
<b>Rank: </b> {token.rank}
<b>MarketCap: </b>{market_cap/1000000:.1f}M
<b>Timeframe: </b> {token.timeframe}
<b>Last Swing High:</b> {last_swing_high}
<b>Date: </b> {date}
<b>Threshold: </b> {token.percent_change_ema}%
<b>Percent Drop: </b>{percent_drop:.2f}%
''',parse_mode='HTML',reply_markup=get_inline_kb(token))
                    await asyncio.sleep(0.5)
         

            await asyncio.sleep(120)

    except asyncio.CancelledError:
        await bybit_client.close()
        raise










