"""Watchlist API Routes with live indicators and snapshot prices."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Watchlist
from app.database.session import get_db
from app.market.data_fetcher import data_fetcher
from app.ranking.engine import recommendation_engine
from app.utils.cache import cache
from app.utils.logger import logger

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])


class WatchlistAddRequest(BaseModel):
    symbol: str
    holding_period: Optional[str] = "3-5 days"
    notes: Optional[str] = ""


import asyncio

@router.get("")
async def get_watchlist(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Watchlist).order_by(Watchlist.added_at.desc()))
    items = result.scalars().all()

    if not items:
        return []

    enriched_items = []
    uncached_symbols = []

    for item in items:
        sym = item.symbol.upper()
        cache_key = f"quote:{sym}"
        cached = await cache.get(cache_key)

        w_price = item.watchlist_price or 0.0
        if cached and cached.get("ltp"):
            c_price = float(cached["ltp"])
        else:
            c_price = w_price
            uncached_symbols.append(sym)

        target = round(c_price * 1.05, 2)
        sl = round(c_price * 0.95, 2)
        bullish_pct = 65.0 if c_price >= w_price else 45.0
        holding = item.holding_period or "3-5 days"
        date_str = item.added_at.strftime("%d/%m/%Y") if item.added_at else ""

        enriched_items.append(
            {
                "id": item.id,
                "symbol": sym,
                "name": item.name,
                "watchlist_price": round(float(w_price), 2),
                "current_price": round(float(c_price), 2),
                "bullish_pct": round(float(bullish_pct), 1),
                "holding_period": holding,
                "added_at_date": date_str,
                "target_price": target,
                "stop_loss": sl,
                "added_at": item.added_at.isoformat(),
                "notes": item.notes,
            }
        )

    # Spawn background async task to populate/refresh quote cache without blocking user HTTP request
    if uncached_symbols:
        asyncio.create_task(data_fetcher.fetch_multiple_quotes_background(uncached_symbols))

    return enriched_items


@router.post("")
async def add_to_watchlist(req: WatchlistAddRequest, db: AsyncSession = Depends(get_db)):
    sym = req.symbol.upper().strip()
    existing = await db.execute(select(Watchlist).where(Watchlist.symbol == sym))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"{sym} is already on the watchlist")

    # Fetch current price at the moment of adding to watchlist
    quote = await data_fetcher.fetch_quote(sym)
    if quote and quote.ltp > 0:
        added_price = quote.ltp
    else:
        ohlcv = await data_fetcher.fetch_ohlcv(sym, period="5d")
        added_price = float(ohlcv.closes[-1]) if ohlcv and ohlcv.closes else 0.0

    holding = req.holding_period or "3-5 days"
    item = Watchlist(
        symbol=sym,
        name=sym,
        watchlist_price=round(added_price, 2),
        holding_period=holding,
        notes=req.notes,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{symbol}")
async def remove_from_watchlist(symbol: str, db: AsyncSession = Depends(get_db)):
    sym = symbol.upper().strip()
    result = await db.execute(select(Watchlist).where(Watchlist.symbol == sym))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail=f"{sym} not found on watchlist")

    await db.delete(item)
    await db.commit()
    return {"message": f"Removed {sym} from watchlist"}
