"""Stock Analysis API Routes."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from app.ranking.engine import recommendation_engine
from app.utils.logger import logger

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.get("/{symbol}")
async def analyze_stock(symbol: str, skip_ai: bool = Query(default=False)):
    rec = await recommendation_engine.analyze_stock(symbol.upper(), skip_ai=skip_ai)
    if not rec:
        raise HTTPException(status_code=404, detail=f"Analysis failed for symbol {symbol}")
    return rec
