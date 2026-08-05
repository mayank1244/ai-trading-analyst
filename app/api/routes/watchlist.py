"""Watchlist API Routes with live indicators and snapshot prices."""

import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Watchlist
from app.database.session import get_db
from app.market.data_fetcher import QuoteData, data_fetcher
from app.utils.logger import logger

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])


class WatchlistAddRequest(BaseModel):
    symbol: str
    holding_period: Optional[str] = "3-5 days"
    notes: Optional[str] = ""


@router.get("")
async def get_watchlist(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Watchlist).order_by(Watchlist.added_at.desc()))
    items = result.scalars().all()

    if not items:
        return []

    # Concurrently fetch live real-time market quotes for all watchlist symbols
    quote_results = await asyncio.gather(
        *[data_fetcher.fetch_quote(item.symbol.upper()) for item in items],
        return_exceptions=True
    )

    enriched_items = []
    for item, q in zip(items, quote_results):
        sym = item.symbol.upper()
        w_price = float(item.watchlist_price or 0.0)

        # Extract live current market price
        if isinstance(q, QuoteData) and q and q.ltp > 0:
            c_price = float(q.ltp)
        else:
            c_price = w_price

        # Calculate live price return since watchlist addition
        if w_price > 0:
            p_diff_pct = ((c_price - w_price) / w_price) * 100.0
        else:
            p_diff_pct = 0.0

        # Dynamic live bullish percentage score (ranges between 15% - 96%)
        bullish_pct = round(min(max(55.0 + (p_diff_pct * 2.5), 15.0), 96.0), 1)

        # Live technical target (+7.5% from current) and Stop Loss (-3.5% from current)
        target = round(c_price * 1.075, 2)
        sl = round(c_price * 0.965, 2)

        holding = item.holding_period or "3-5 days"
        date_str = item.added_at.strftime("%d/%m/%Y") if item.added_at else ""

        enriched_items.append(
            {
                "id": item.id,
                "symbol": sym,
                "name": item.name,
                "watchlist_price": round(w_price, 2),
                "current_price": round(c_price, 2),
                "bullish_pct": bullish_pct,
                "holding_period": holding,
                "added_at_date": date_str,
                "target_price": target,
                "stop_loss": sl,
                "added_at": item.added_at.isoformat() if item.added_at else "",
                "notes": item.notes,
            }
        )

    return enriched_items


@router.post("")
async def add_to_watchlist(req: WatchlistAddRequest, db: AsyncSession = Depends(get_db)):
    sym = req.symbol.upper().strip()
    existing = await db.execute(select(Watchlist).where(Watchlist.symbol == sym))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"{sym} is already on the watchlist")

    # Fetch current price at the exact moment of adding to snapshot
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
