from client_api.base import BaseClient
from config import Config

class CryptoRankCLient(BaseClient):
    def __init__(self,base_url):
        super().__init__(base_url)
        self.base_url = base_url




    async def get_token_info(self,symbol,config:Config):
        """Получает описание токена с CryptoRank API v2."""
        headers = {"X-Api-Key": config.api.crypto_rank_api_key}
        params = {"symbol": symbol}

        result=await self.make_request(method='GET',url='/v2/currencies/',params=params,headers=headers)
        try:
            return result.get("data")[0]
        except Exception as e:
            return f"Ошибка API:{e}"