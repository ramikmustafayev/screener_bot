from .settings import settings_router
from .start import start_router
from .screener import screener_router
from .token import token_router

routers_list=[
    settings_router,
    start_router,
    screener_router,
    token_router,
]


__all__=[routers_list]