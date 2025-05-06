from client_api.bybit_api import BybitClient
from client_api.schemas import Token as TokenSchema
from database.models import Token

tickers_to_exclude = {
    'SHIBUSDT', 'PEPEUSDT', 'TRUPMUSDT', 'BONKUSDT', 'FLOKIUSDT', 'BRETTUSDT', 'WIFUSDT',
    'SPXUSDT', 'TURBOUSDT', 'POPCATUSDT', 'AI16ZUSDT', 'MEWUSDT', 'MOGUSDT', 'BABYDOGEUSDT', 'PNUTUSDT',
    'ORDIUSDT', 'TOSHIUSDT', 'AIXBTUSDT', 'BOMEUSDT', 'NEIROUSDT', 'SATSUSDT', 'ANIMEUSDT',
    'BTC3LUSDT', 'NEIROCTOUSDT', 'DOP1USDT', 'ETH3LUSDT', 'LUNAIUSDT', 'EGP1USDT', 'BTC3SUSDT',
    'ETH3SUSDT', 'MYROUSDT', 'HPOS10IUSDT', 'CATBNBUSDT', 'GALFTUSDT','MEMEFIUSDT','MEMEUSDT','USDYUSDT',
    'USDTBUSDT','USDRUSDT','USDQUSDT','USDEUSDT','USDDUSDT','USDCUSDT','DAIUSDT','PYUSDUSDT','TUSDUSDT',
    'ZEREBROUSDT','XUSDT','PIXFIUSDT','PAWSUSDT','RVNUSDT','VINUUSDT','COQUSDT','KSMUSDT',
    'LADYSUSDT','PEOPLEUSDT','DEGENUSDT','TOKENUSDT','PONKEUSDT','LUCEUSDT','GUMMYUSDT','CATSUSDT',
    'FOXYUSDT','LUNAUSDT','SENDUSDT','PERPUSDT','LEVERUSDT','RATSUSDT','WENUSDT','GAMEUSDT','CATIUSDT',
    'BANUSDT','SUNDOGUSDT','PUFFUSDT','GOATUSDT','DOGSUSDT','PSGUSDT','CITYUSDT','JUVUSDT','UNIUSDT','BNBUSDT',
    'AAVEUSDT','JUPUSDT','CAKEUSDT','DYDXUSDT','1INCHUSDT','SUSHIUSDT','GMXUSDT','RUNEUSDT','PPTUSDT',
    'KCSUSDT','INJUSDT','KAVAUSDT','WBTCUSDT','BTCUSDT','ETHUSDT','UMAUSDT','COMPUSDT','C98USDT','SUNUSDT',
    'OMUSDT','CHILLGUYUSDT','AFCUSDT','INTERUSDT'
    
}

async def update_database(bybit_client:BybitClient,tokens_repo,user):
    try:
        tokens:list[TokenSchema]=await bybit_client.fetch_spot_symbols()
    except Exception as e:
        print('Error fetching tokens:', e)
        await bybit_client.close()

    tokens = [token for token in tokens if token.ticker not in tickers_to_exclude]

    if await tokens_repo.is_table_empty(user_id=user.id):
        tokens_for_pump=[Token(ticker=token.ticker,price_change=token.price_change*100,volume_per_day=token.volume_per_day,last_price=token.last_price,sygnal_per_day=0,pump_percent=2,pump_period=15,user_id=user.id,is_in_blacklist=False,is_muted=False) for token in tokens]
        await tokens_repo.add_all(tokens_for_pump)

    else:
        for token in tokens:
            token_from_db:Token=await tokens_repo.get_one_or_none(ticker=token.ticker,user_id=user.id)
            
            if token_from_db is None:
                new_token:Token= await tokens_repo.add(ticker=token.ticker,last_price=token.last_price,sygnal_per_day=0,pump_percent=2,price_change=token.price_change*100,volume_per_day=token.volume_per_day,pump_period=15,user_id=user.id,is_in_blacklist=False,is_muted=False)
                token_from_db=new_token
            
            
            if not token_from_db.is_in_blacklist:
                await tokens_repo.update({'ticker':token.ticker,'user_id':user.id},{'last_price':token.last_price, 'price_change':token.price_change*100,'volume_per_day':token.volume_per_day})
            

        


