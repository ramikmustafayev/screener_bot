import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timedelta
from database.models.tokens import Token
from database.models.users import User
from database.repo.requests import RequestsRepo
from keyboards.all_keyboards import get_inline_kb
from client_api.bybit_api import BybitClient
from client_api.schemas import Token as TokenSchema
from services.ema_calculator import calculate_ema




async def track_prices(message,repo:RequestsRepo,user:User,config):
    base_url = config.api.bybit_url
    bybit_client = BybitClient(base_url)
    token_repo = repo.tokens

 

    async def safe_fetch_klines(token:Token):
        try:
            return await bybit_client.fetch_klines(token.ticker, token.timeframe, 50)
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
                token_ema_list = list(executor.map(calculate_ema, results))

           
            for token_data in token_ema_list:
                ema = token_data.get('ema')
                price = token_data.get('last_price')
                symbol = token_data.get('symbol')
                token:Token=await token_repo.get_one_or_none(ticker=symbol,user_id=user.id)
                if ema > 0 and price < ema * (1-token.percent_change_ema/100):
                    
                    market_cap=token.circulating_supply*price
                    percent_drop = round((ema - price) / ema * 100, 2)
                    await message.answer(f'''<b>Symbol: </b> {symbol}
<b>Rank: </b> {token.rank}
<b>MarketCap: </b>{market_cap/1000000:.1f}M
<b>Timeframe: </b> {token.timeframe}
<b>Threshold: </b> {token.percent_change_ema}%
<b>Percent Drop: </b>{percent_drop:.2f}%
''',parse_mode='HTML',reply_markup=get_inline_kb(token))
                    await asyncio.sleep(0.2)
         

            await asyncio.sleep(30)

    except asyncio.CancelledError:
        await bybit_client.close()
        raise










