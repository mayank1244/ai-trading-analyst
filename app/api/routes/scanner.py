"""Market Scanner API Routes."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException

from app.scanner.market_scanner import market_scanner
from app.utils.logger import logger

router = APIRouter(prefix="/scanner", tags=["Scanner"])


@router.get("/run")
async def run_scanner():
    try:
        output = await market_scanner.scan_universe()
        return output
    except Exception as exc:
        logger.error("Scanner API error: {}", exc)
        raise HTTPException(status_code=500, detail=str(exc))
