from .start import start_router
from .screener import screener_router
from .token import token_router
from .callback_handlers import callback_router
from .sql_presets import sql_preset_router

routers_list=[
    start_router,
    screener_router,
    token_router,
    callback_router,
    sql_preset_router
]


__all__=[routers_list]