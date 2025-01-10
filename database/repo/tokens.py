from database.repo.base import BaseRepo
from database.models import TokenForDump,TokenForPump


    

class PumpTokensRepo(BaseRepo):
    model=TokenForPump


class DumpTokensRepo(BaseRepo):
    model=TokenForDump
    
    


   
        