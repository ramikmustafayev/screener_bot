import asyncio
import time
from functools import wraps

def rate_limited(max_calls: int, period: float):
    calls = []

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            now = time.monotonic()

            # Очищаем старые вызовы
            nonlocal calls
            calls = [call for call in calls if now - call < period]
            if len(calls) >= max_calls:
               
                sleep_time = period - (now - calls[0])
                await asyncio.sleep(sleep_time)

            calls.append(time.monotonic())
            return await func(*args, **kwargs)
        return wrapper

    return decorator