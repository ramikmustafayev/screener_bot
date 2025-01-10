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
class API:
    url:str

    @staticmethod
    def from_env(env: AutoConfig):
        url=env('BYBIT_URL')
        return API(url=url)
    

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
  