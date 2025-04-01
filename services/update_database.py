from datetime import datetime
from client_api.bybit_api import BybitClient
from client_api.schemas import Token as TokenSchema
from database.models import Token

async def update_database(config,tokens_repo,user):
    try:
        base_url=config.api.bybit_url
        bybit_client=BybitClient(base_url)
        tokens:list[TokenSchema]=await bybit_client.fetch_spot_symbols()
    finally:
        await bybit_client.close()

    for token in tokens:
        ticker_name=token.ticker
        current_price=token.last_price
        token_from_db:Token=await tokens_repo.get_one_or_none(ticker=ticker_name,user_id=user.id)
        
        if token_from_db is None:
            new_token:Token= await tokens_repo.add(ticker=token.ticker,last_price=token.last_price,sygnal_per_day=0,pump_percent=2,pump_period=15,user_id=user.id,is_in_blacklist=False,is_interesting=False)
            token_from_db=new_token
        
        

        await tokens_repo.update({'ticker':ticker_name,'user_id':user.id},{'last_price':current_price})
        
        
        

        