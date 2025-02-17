from database.repo.requests import RequestsRepo

async def reset_column(session_pool):
    async with session_pool() as session:
            repo=RequestsRepo(session)
            pump_tokens=repo.pump_tokens
            await pump_tokens.update({},{'sygnal_per_day':0})