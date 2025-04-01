from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from database.repo.users import UserRepo
from database.repo.tokens import TokensRepo
from database.repo.watch_list import WatchListRepo

@dataclass
class RequestsRepo:

    session:AsyncSession



    @property
    def users(self):
        return UserRepo(self.session)
    

    @property
    def tokens(self):
        return TokensRepo(self.session)
    

    
    @property
    def watchlist(self):
        return WatchListRepo(self.session)
    

