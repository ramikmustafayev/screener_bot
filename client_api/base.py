import asyncio
from aiohttp import ClientSession,TCPConnector,ClientError

class BaseClient:
    def __init__(self,base_url):
        self._base_url = base_url
        self._session:ClientSession=None



    async def _get_session(self)->ClientSession:
        if self._session is None:
            connector=TCPConnector(ssl_context=False)
            self._session = ClientSession(base_url=self._base_url,connector=connector)

        return self._session



    async def make_request(self,method,url,params=None,json=None,headers=None,data=None):
        
         
        session=await self._get_session()
        async with session.request(method, url, params=params, json=json, headers=headers, data=data) as response:
            status=response.status
            if status != 200:
                s=await response.text()
                raise ClientError(f"Got status {status} for {method} {url}: {s}")
            try:
                result=await response.json()
            except Exception as e:
                result={}
        return result
        
     
        
    async def close(self):
        if not self._session:
            return
        
        if self._session.closed:
            return
        

        await self._session.close()
        await asyncio.sleep(0.25)
            

    
    

    
