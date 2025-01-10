from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from database.repo.users import UserRepo
from database.repo.tokens import PumpTokensRepo,DumpTokensRepo
from database.repo.watch_list import WatchListRepo
from database.repo.settings import SettingsRepo
@dataclass
class RequestsRepo:

    session:AsyncSession



    @property
    def users(self):
        return UserRepo(self.session)
    

    @property
    def pump_tokens(self):
        return PumpTokensRepo(self.session)
    
    @property
    def dump_tokens(self):
        return DumpTokensRepo(self.session)
    
    @property
    def watchlist(self):
        return WatchListRepo(self.session)
    
    @property
    def settings(self):
        return SettingsRepo(self.session)