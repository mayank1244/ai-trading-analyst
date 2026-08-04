"""Market Data API Routes."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from app.market.data_fetcher import data_fetcher
from app.market.nse_universe import NSE_UNIVERSE, get_all_sectors, get_all_symbols
from app.utils.logger import logger

router = APIRouter(prefix="/market", tags=["Market Data"])


@router.get("/overview")
async def get_market_overview():
    try:
        indices = await data_fetcher.fetch_index_data()
        idx_list = [
            {"name": name, "value": item.value, "change": item.change, "change_pct": item.change_pct}
            for name, item in indices.items()
        ]
        return {
            "indices": idx_list,
            "sectors": get_all_sectors(),
            "status": "ok",
        }
    except Exception as exc:
        logger.error("Error in /market/overview: {}", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/indices")
async def get_indices():
    indices = await data_fetcher.fetch_index_data()
    return [
        {"name": name, "value": item.value, "change": item.change, "change_pct": item.change_pct}
        for name, item in indices.items()
    ]


@router.get("/stocks")
async def get_stocks():
    return [
        {"symbol": s, "name": info.name, "sector": info.sector, "category": info.market_cap_category}
        for s, info in NSE_UNIVERSE.items()
    ]


@router.get("/quote/{symbol}")
async def get_quote(symbol: str):
    quote = await data_fetcher.fetch_quote(symbol)
    if not quote:
        raise HTTPException(status_code=404, detail=f"Quote not found for {symbol}")
    return quote
