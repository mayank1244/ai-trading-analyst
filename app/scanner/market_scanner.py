"""Market Scanner module."""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from app.config.settings import settings
from app.market.data_fetcher import data_fetcher
from app.market.nse_universe import get_nifty50_symbols, NSE_UNIVERSE
from app.patterns.candlestick import pattern_detector
from app.price_action.detector import price_action_detector
from app.risk.calculator import risk_calculator
from app.strategy.scoring import scoring_engine
from app.technical.indicators import indicators
from app.utils.logger import logger


@dataclass
class ScanResult:
    symbol: str
    name: str
    sector: str
    current_price: float
    change_pct: float
    volume: int
    quant_score: float
    recommendation: str
    confidence: float
    entry_price: float
    stop_loss: float
    target_1: float
    target_2: float
    risk_reward: float
    holding_period: str
    bullish_signals: List[str] = field(default_factory=list)
    bearish_signals: List[str] = field(default_factory=list)
    is_breakout: bool = False
    is_near_support: bool = False
    is_high_volume: bool = False
    pattern_name: Optional[str] = None
    technical_summary: str = ""


@dataclass
class ScannerOutput:
    top_buy: List[ScanResult] = field(default_factory=list)
    top_risk_buy: List[ScanResult] = field(default_factory=list)
    intraday_stocks: List[ScanResult] = field(default_factory=list)
    top_sell: List[ScanResult] = field(default_factory=list)
    swing_trades: List[ScanResult] = field(default_factory=list)
    momentum_stocks: List[ScanResult] = field(default_factory=list)
    breakout_stocks: List[ScanResult] = field(default_factory=list)
    high_volume_stocks: List[ScanResult] = field(default_factory=list)
    total_scanned: int = 0
    timestamp: Optional[str] = None


class MarketScanner:
    async def analyze_single_stock(
        self, symbol: str, index_data: dict = {}, sector_scores: dict = {}
    ) -> Optional[ScanResult]:
        try:
            ohlcv = await data_fetcher.fetch_ohlcv(symbol, period="1y", interval="1d")
            if ohlcv is None or len(ohlcv.df) < 30:
                return None

            df, ind_res = indicators.compute_all(ohlcv.df)
            pa_res = price_action_detector.analyze(df)
            pat_res = pattern_detector.detect_all(df)

            stock_info = NSE_UNIVERSE.get(symbol)
            sector = stock_info.sector if stock_info else "General"
            name = stock_info.name if stock_info else symbol

            quant_res = scoring_engine.compute(
                df, ind_res, pa_res, pat_res, sector, sector_scores, index_data
            )

            rec_label = "HOLD"
            if quant_res.total_score >= 80:
                rec_label = "STRONG_BUY"
            elif quant_res.total_score >= 65:
                rec_label = "BUY"
            elif quant_res.total_score >= 50:
                rec_label = "WATCHLIST"
            elif quant_res.total_score <= 35:
                rec_label = "SELL"

            risk_res = risk_calculator.compute(df, rec_label)

            last_close = float(df["Close"].iloc[-1])
            prev_close = float(df["Close"].iloc[-2]) if len(df) > 1 else last_close
            chg_pct = (last_close - prev_close) / prev_close * 100

            top_pat = pat_res.detected_patterns[0].name if pat_res.detected_patterns else None

            return ScanResult(
                symbol=symbol,
                name=name,
                sector=sector,
                current_price=float(last_close),
                change_pct=float(round(chg_pct, 2)),
                volume=int(df["Volume"].iloc[-1]),
                quant_score=float(round(quant_res.total_score, 1)),
                recommendation=rec_label,
                confidence=float(round(quant_res.total_score, 1)),
                entry_price=float(risk_res.entry_price),
                stop_loss=float(risk_res.stop_loss),
                target_1=float(risk_res.target_1),
                target_2=float(risk_res.target_2),
                risk_reward=float(risk_res.risk_reward_1),
                holding_period=str(risk_res.holding_period),
                bullish_signals=[str(s) for s in quant_res.bullish_signals],
                bearish_signals=[str(s) for s in quant_res.bearish_signals],
                is_breakout=bool(pa_res.is_breakout),
                is_near_support=bool(pa_res.is_near_support),
                is_high_volume=bool(df["Volume"].iloc[-1] > 1.5 * df["Volume"].tail(20).mean()),
                pattern_name=str(top_pat) if top_pat else None,
                technical_summary=str(quant_res.technical_summary),
            )
        except Exception as exc:
            logger.error("Scanner error on {}: {}", symbol, exc)
            return None

    async def scan_universe(self, symbols: Optional[List[str]] = None) -> ScannerOutput:
        target_symbols = symbols if symbols else get_nifty50_symbols()
        index_data = await data_fetcher.fetch_index_data()

        tasks = [self.analyze_single_stock(s, index_data) for s in target_symbols]
        raw_results = await asyncio.gather(*tasks)
        results = [r for r in raw_results if r is not None]

        top_buy = sorted(
            [r for r in results if r.recommendation in ["BUY", "STRONG_BUY"]],
            key=lambda x: x.quant_score,
            reverse=True,
        )

        # Top 20 Risk Buy: Price ₹100–₹5000, Bullish Score > 60%, Holding Period 3-5 days
        risk_buys = sorted(
            [
                r for r in results
                if 100.0 <= r.current_price <= 5000.0
                and r.quant_score > 60.0
                and "3-5 days" in r.holding_period
            ],
            key=lambda x: x.quant_score,
            reverse=True,
        )

        if not risk_buys:
            risk_buys = sorted(
                [
                    r for r in results
                    if 100.0 <= r.current_price <= 5000.0
                    and r.quant_score > 60.0
                ],
                key=lambda x: x.quant_score,
                reverse=True,
            )

        # Intraday Bullish: Score > 55%, positive momentum, tight SL/Target, holding period = Intraday (Same Day)
        intraday_list = []
        for r in sorted(results, key=lambda x: (x.quant_score * 0.7 + x.change_pct * 3), reverse=True):
            if r.quant_score >= 52.0:
                cp = r.current_price
                intraday_r = ScanResult(
                    symbol=r.symbol,
                    name=r.name,
                    sector=r.sector,
                    current_price=cp,
                    change_pct=r.change_pct,
                    volume=r.volume,
                    quant_score=r.quant_score,
                    recommendation="BUY" if r.quant_score >= 60 else "WATCHLIST",
                    confidence=r.confidence,
                    entry_price=cp,
                    stop_loss=round(cp * 0.992, 2), # 0.8% tight intraday SL
                    target_1=round(cp * 1.012, 2),  # 1.2% intraday T1
                    target_2=round(cp * 1.025, 2),  # 2.5% intraday T2
                    risk_reward=1.5,
                    holding_period="Intraday (Same Day)",
                    bullish_signals=r.bullish_signals,
                    bearish_signals=r.bearish_signals,
                    is_breakout=r.is_breakout,
                    is_near_support=r.is_near_support,
                    is_high_volume=r.is_high_volume,
                    pattern_name=r.pattern_name,
                    technical_summary=r.technical_summary,
                )
                intraday_list.append(intraday_r)

        top_sell = sorted(
            [r for r in results if r.recommendation in ["SELL", "STRONG_SELL"]],
            key=lambda x: x.quant_score,
        )
        breakouts = [r for r in results if r.is_breakout]
        momentum = sorted(results, key=lambda x: x.change_pct, reverse=True)
        high_vol = [r for r in results if r.is_high_volume]

        return ScannerOutput(
            top_buy=top_buy[:20],
            top_risk_buy=risk_buys[:20],
            intraday_stocks=intraday_list[:20],
            top_sell=top_sell[:20],
            swing_trades=top_buy[:10],
            momentum_stocks=momentum[:10],
            breakout_stocks=breakouts[:10],
            high_volume_stocks=high_vol[:10],
            total_scanned=len(results),
            timestamp=datetime.now().isoformat(),
        )


market_scanner = MarketScanner()
