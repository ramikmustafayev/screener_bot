from dataclasses import dataclass
from decouple import AutoConfig,config
from sqlalchemy.engine.url import URL



@dataclass
class DbConfig:
    database: str
 


    def construct_sqlalchemy_url(self, driver="aiosqlite"):
        uri=URL.create(
            drivername=f'sqlite+{driver}',
            database=self.database
        )

        return uri.render_as_string(hide_password=False)
    

    @staticmethod
    def from_env(env:AutoConfig):
        database = env("DATABASE_NAME")
        return DbConfig(database=database)
    




@dataclass
class TgBot:
    token: str
    


    @staticmethod
    def from_env(env: AutoConfig):
        token = env("TOKEN")
        return TgBot(token=token)
    
@dataclass
    
@dataclass
class API:
    bybit_url:str
    crypto_rank_url:str
    crypto_rank_api_key:str

    @staticmethod
    def from_env(env: AutoConfig):
        bybit_url=env('BYBIT_URL')
        crypto_rank_url=env('CRYPTORANK_URL')
        crypto_rank_api_key=env('CRYPTORANK_API_KEY')
        return API(bybit_url=bybit_url,crypto_rank_url=crypto_rank_url,crypto_rank_api_key=crypto_rank_api_key)
    

@dataclass
class Config:
    tg_bot: TgBot
    db:DbConfig
    api:API




def load_config(path:str=None):
    return Config(
        tg_bot=TgBot.from_env(config),
        db=DbConfig.from_env(config),
        api=API.from_env(config)
    )
  