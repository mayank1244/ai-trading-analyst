from app.api.routes.analysis import router as analysis_router
from app.api.routes.chat import router as chat_router
from app.api.routes.market import router as market_router
from app.api.routes.scanner import router as scanner_router
from app.api.routes.watchlist import router as watchlist_router

__all__ = [
    "market_router",
    "analysis_router",
    "scanner_router",
    "watchlist_router",
    "chat_router",
]
