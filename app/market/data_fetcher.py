"""NSE Market Data Fetcher using yfinance."""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import yfinance as yf

from app.config.settings import settings
from app.market.nse_universe import INDICES, NSE_UNIVERSE, get_all_symbols
from app.utils.cache import cache
from app.utils.logger import logger


@dataclass
class OHLCVData:
    symbol: str
    dates: List[datetime]
    opens: List[float]
    highs: List[float]
    lows: List[float]
    closes: List[float]
    volumes: List[int]
    df: pd.DataFrame


@dataclass
class QuoteData:
    symbol: str
    name: str
    ltp: float
    change: float
    change_pct: float
    volume: int
    open: float
    high: float
    low: float
    prev_close: float
    market_cap: Optional[float]
    week_52_high: float
    week_52_low: float
    pe_ratio: Optional[float]
    eps: Optional[float]
    timestamp: datetime


@dataclass
class IndexData:
    symbol: str
    name: str
    value: float
    change: float
    change_pct: float
    timestamp: datetime


class NSEDataFetcher:
    def _to_yf_symbol(self, symbol: str) -> str:
        if symbol.startswith("^"):
            return symbol
        return f"{symbol}.NS" if not symbol.endswith(".NS") else symbol

    async def fetch_ohlcv(
        self, symbol: str, period: str = "1y", interval: str = "1d"
    ) -> Optional[OHLCVData]:
        cache_key = f"ohlcv:{symbol}:{period}:{interval}"
        cached = await cache.get(cache_key)
        if cached:
            try:
                df = pd.read_json(cached["df"])
                return OHLCVData(
                    symbol=symbol,
                    dates=[pd.to_datetime(d) for d in cached["dates"]],
                    opens=cached["opens"],
                    highs=cached["highs"],
                    lows=cached["lows"],
                    closes=cached["closes"],
                    volumes=cached["volumes"],
                    df=df,
                )
            except Exception:
                pass

        try:
            yf_sym = self._to_yf_symbol(symbol)
            ticker = yf.Ticker(yf_sym)
            df = await asyncio.to_thread(ticker.history, period=period, interval=interval)

            if df.empty or len(df) < 5:
                logger.warning("Empty or insufficient OHLCV data for {}", symbol)
                return None

            df = df.dropna()
            df = df[df["Close"] > 0]

            dates = [d.to_pydatetime() for d in df.index]
            opens = df["Open"].astype(float).tolist()
            highs = df["High"].astype(float).tolist()
            lows = df["Low"].astype(float).tolist()
            closes = df["Close"].astype(float).tolist()
            volumes = df["Volume"].astype(int).tolist()

            res = OHLCVData(
                symbol=symbol,
                dates=dates,
                opens=opens,
                highs=highs,
                lows=lows,
                closes=closes,
                volumes=volumes,
                df=df,
            )

            await cache.set(
                cache_key,
                {
                    "dates": [d.isoformat() for d in dates],
                    "opens": opens,
                    "highs": highs,
                    "lows": lows,
                    "closes": closes,
                    "volumes": volumes,
                    "df": df.to_json(),
                },
                ttl=settings.MARKET_DATA_CACHE_TTL,
            )
            return res
        except Exception as exc:
            logger.error("Error fetching OHLCV for {}: {}", symbol, exc)
            return None

    async def fetch_multiple_ohlcv(
        self, symbols: List[str], period: str = "1y", interval: str = "1d", max_workers: int = 4
    ) -> Dict[str, OHLCVData]:
        sem = asyncio.Semaphore(max_workers)

        async def _fetch(s: str):
            async with sem:
                return s, await self.fetch_ohlcv(s, period, interval)

        tasks = [_fetch(s) for s in symbols]
        results = await asyncio.gather(*tasks)
        return {s: data for s, data in results if data is not None}

    async def fetch_quote(self, symbol: str) -> Optional[QuoteData]:
        cache_key = f"quote:{symbol}"
        cached = await cache.get(cache_key)
        if cached:
            try:
                return QuoteData(
                    symbol=cached["symbol"],
                    name=cached["name"],
                    ltp=cached["ltp"],
                    change=cached["change"],
                    change_pct=cached["change_pct"],
                    volume=cached["volume"],
                    open=cached["open"],
                    high=cached["high"],
                    low=cached["low"],
                    prev_close=cached["prev_close"],
                    market_cap=cached.get("market_cap"),
                    week_52_high=cached["week_52_high"],
                    week_52_low=cached["week_52_low"],
                    pe_ratio=cached.get("pe_ratio"),
                    eps=cached.get("eps"),
                    timestamp=pd.to_datetime(cached["timestamp"]),
                )
            except Exception:
                pass

        try:
            yf_sym = self._to_yf_symbol(symbol)
            ticker = yf.Ticker(yf_sym)
            fast_info = getattr(ticker, "fast_info", {})
            
            ltp = float(fast_info.get("lastPrice") or fast_info.get("regularMarketPrice") or 0.0)
            prev_close = float(fast_info.get("previousClose") or fast_info.get("regularMarketPreviousClose") or ltp)

            if not ltp or ltp <= 0:
                info = await asyncio.to_thread(lambda: ticker.info)
                ltp = float(info.get("regularMarketPrice") or info.get("currentPrice") or 0.0)
                name = info.get("longName") or info.get("shortName") or symbol
                vol = int(info.get("regularMarketVolume") or info.get("volume") or 0)
                op = float(info.get("regularMarketOpen") or info.get("open") or ltp)
                hi = float(info.get("regularMarketDayHigh") or info.get("dayHigh") or ltp)
                lo = float(info.get("regularMarketDayLow") or info.get("dayLow") or ltp)
                mcap = info.get("marketCap")
                w52h = float(info.get("fiftyTwoWeekHigh") or ltp)
                w52l = float(info.get("fiftyTwoWeekLow") or ltp)
                pe = info.get("trailingPE")
                eps_val = info.get("trailingEps")
            else:
                name = symbol
                vol = int(fast_info.get("lastVolume") or 0)
                op = float(fast_info.get("open") or ltp)
                hi = float(fast_info.get("dayHigh") or ltp)
                lo = float(fast_info.get("dayLow") or ltp)
                mcap = fast_info.get("marketCap")
                w52h = float(fast_info.get("yearHigh") or ltp)
                w52l = float(fast_info.get("yearLow") or ltp)
                pe = None
                eps_val = None

            change = ltp - prev_close
            change_pct = (change / prev_close * 100) if prev_close else 0.0

            quote_res = QuoteData(
                symbol=symbol,
                name=name,
                ltp=ltp,
                change=change,
                change_pct=change_pct,
                volume=vol,
                open=op,
                high=hi,
                low=lo,
                prev_close=prev_close,
                market_cap=mcap,
                week_52_high=w52h,
                week_52_low=w52l,
                pe_ratio=pe,
                eps=eps_val,
                timestamp=datetime.now(),
            )

            await cache.set(
                cache_key,
                {
                    "symbol": symbol,
                    "name": name,
                    "ltp": ltp,
                    "change": change,
                    "change_pct": change_pct,
                    "volume": vol,
                    "open": op,
                    "high": hi,
                    "low": lo,
                    "prev_close": prev_close,
                    "market_cap": mcap,
                    "week_52_high": w52h,
                    "week_52_low": w52l,
                    "pe_ratio": pe,
                    "eps": eps_val,
                    "timestamp": quote_res.timestamp.isoformat(),
                },
                ttl=60,
            )
            return quote_res
        except Exception as exc:
            logger.error("Error fetching quote for {}: {}", symbol, exc)
            return None

    async def fetch_multiple_quotes_background(self, symbols: List[str]) -> None:
        """Background worker to fetch and cache quotes asynchronously."""
        try:
            tasks = [self.fetch_quote(s) for s in symbols]
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as exc:
            logger.error("Background quote fetch error: {}", exc)

    async def fetch_index_data(self) -> Dict[str, IndexData]:
        results = {}
        for name, yf_sym in INDICES.items():
            try:
                ticker = yf.Ticker(yf_sym)
                df = await asyncio.to_thread(ticker.history, period="5d")
                if not df.empty:
                    val = float(df["Close"].iloc[-1])
                    prev = float(df["Close"].iloc[-2]) if len(df) > 1 else val
                    chg = val - prev
                    chg_pct = (chg / prev * 100) if prev else 0.0
                    results[name] = IndexData(
                        symbol=yf_sym,
                        name=name,
                        value=val,
                        change=chg,
                        change_pct=chg_pct,
                        timestamp=datetime.now(),
                    )
            except Exception as exc:
                logger.error("Error fetching index {}: {}", name, exc)
        return results


data_fetcher = NSEDataFetcher()
