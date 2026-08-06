from fastapi import APIRouter

from app.api.routes.analysis import router as analysis_router
from app.api.routes.chat import router as chat_router
from app.api.routes.live_analyzer import router as live_analyzer_router
from app.api.routes.market import router as market_router
from app.api.routes.scanner import router as scanner_router
from app.api.routes.swing_analyzer import router as swing_analyzer_router
from app.api.routes.watchlist import router as watchlist_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(market_router)
api_router.include_router(analysis_router)
api_router.include_router(scanner_router)
api_router.include_router(watchlist_router)
api_router.include_router(chat_router)
api_router.include_router(live_analyzer_router)
api_router.include_router(swing_analyzer_router)

__all__ = ["api_router"]
