from client_api.bybit_api import BybitClient
from client_api.schemas import Token as TokenSchema
from database.models import Token

async def populate_database(config,tokens_repo,user):
    try:
        base_url=config.api.bybit_url
        bybit_client=BybitClient(base_url)
        tokens:list[TokenSchema]=await bybit_client.fetch_spot_symbols()
    finally:
        await bybit_client.close()

    tokens_for_pump=[Token(ticker=token.ticker,last_price=token.last_price,sygnal_per_day=0,pump_percent=0.2,pump_period=15,user_id=user.id,is_in_blacklist=False,is_interesting=False) for token in tokens]
       
    await tokens_repo.add_all(tokens_for_pump)