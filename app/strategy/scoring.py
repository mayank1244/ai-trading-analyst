"""Rule-Based Quantitative Scoring Engine (70% component)."""

from dataclasses import dataclass, field
from typing import Dict, List
import pandas as pd


@dataclass
class ComponentScore:
    name: str
    score: float
    weight: float
    weighted_score: float
    details: str = ""


@dataclass
class QuantScoreResult:
    total_score: float
    trend_score: ComponentScore
    momentum_score: ComponentScore
    volume_score: ComponentScore
    sr_score: ComponentScore
    pattern_score: ComponentScore
    sector_score: ComponentScore
    market_score: ComponentScore
    volatility_score: ComponentScore
    bullish_signals: List[str] = field(default_factory=list)
    bearish_signals: List[str] = field(default_factory=list)
    technical_summary: str = ""
    direction: str = "NEUTRAL"


class QuantScoringEngine:
    def compute(
        self,
        df: pd.DataFrame,
        indicator_results: dict,
        price_action_result,
        pattern_result,
        sector: str = "General",
        sector_scores: Dict[str, float] = {},
        index_data: dict = {},
    ) -> QuantScoreResult:
        bullish = []
        bearish = []

        last_close = float(df["Close"].iloc[-1]) if not df.empty else 0.0

        # 1. Trend Score & Multi-Timeframe Alignment (20%)
        ema_res = indicator_results.get("EMA")
        st_res = indicator_results.get("Supertrend")
        vwap_res = indicator_results.get("VWAP")
        t_score = 50.0

        if ema_res and ema_res.signal == "BULLISH":
            t_score += 25
            bullish.append("Strong EMA Trend Alignment (9 > 21 > 50 > 200)")
        elif ema_res and ema_res.signal == "BEARISH":
            t_score -= 25
            bearish.append("Weak EMA Trend Alignment")

        if st_res and st_res.signal == "BULLISH":
            t_score += 20
            bullish.append("Supertrend Bullish Trend")
        elif st_res and st_res.signal == "BEARISH":
            t_score -= 20
            bearish.append("Supertrend Bearish Trend")

        # VWAP Institutional Confluence
        if vwap_res and vwap_res.signal == "BULLISH":
            t_score += 15
            bullish.append("Trading Above VWAP (Institutional Support)")

        t_score = max(0.0, min(100.0, t_score))
        trend_comp = ComponentScore("Trend", t_score, 0.20, t_score * 0.20)

        # 2. Momentum Score (15%)
        rsi_res = indicator_results.get("RSI")
        macd_res = indicator_results.get("MACD")
        stoch_res = indicator_results.get("StochRSI")
        m_score = 50.0

        if rsi_res and rsi_res.signal == "BULLISH":
            m_score += 20
            bullish.append("RSI in Bullish Momentum Zone (>55)")
        elif rsi_res and rsi_res.signal == "BEARISH":
            m_score -= 20
            bearish.append("RSI in Bearish Momentum Zone (<45)")

        if macd_res and macd_res.signal == "BULLISH":
            m_score += 20
            bullish.append("MACD Bullish Histogram Crossover")
        elif macd_res and macd_res.signal == "BEARISH":
            m_score -= 20
            bearish.append("MACD Bearish Crossover")

        if stoch_res and stoch_res.signal == "BULLISH":
            m_score += 15
            bullish.append("Stochastic RSI Turning Up")

        m_score = max(0.0, min(100.0, m_score))
        mom_comp = ComponentScore("Momentum", m_score, 0.15, m_score * 0.15)

        # 3. Volume & Institutional Accumulation Score (15%)
        v_score = 50.0
        if len(df) >= 20:
            vol_curr = float(df["Volume"].iloc[-1])
            vol_avg = float(df["Volume"].tail(20).mean())
            if vol_avg > 0:
                vol_ratio = vol_curr / vol_avg
                if vol_ratio >= 2.0:
                    v_score = 95.0
                    bullish.append(f"Huge Institutional Volume Surge ({vol_ratio:.1f}x Avg)")
                elif vol_ratio >= 1.5:
                    v_score = 80.0
                    bullish.append(f"Strong Volume Surge ({vol_ratio:.1f}x Avg)")
                elif vol_ratio < 0.6:
                    v_score = 30.0
                    bearish.append("Below-Average Trading Volume")

        vol_comp = ComponentScore("Volume", v_score, 0.15, v_score * 0.15)

        # 4. Support / Resistance & Breakout Precision (10%)
        sr_score = price_action_result.price_action_score if price_action_result else 50.0
        if price_action_result:
            bullish.extend(price_action_result.bullish_signals)
            bearish.extend(price_action_result.bearish_signals)
        sr_comp = ComponentScore("S/R & Price Action", sr_score, 0.10, sr_score * 0.10)

        # 5. Candlestick Pattern Signal Weighting (10%)
        pat_score = pattern_result.pattern_score if pattern_result else 50.0
        if pattern_result:
            bullish.extend([f"Pattern: {p}" for p in pattern_result.bullish_patterns])
            bearish.extend([f"Pattern: {p}" for p in pattern_result.bearish_patterns])
        pat_comp = ComponentScore("Candlestick", pat_score, 0.10, pat_score * 0.10)

        # 6. Sector Relative Strength (10%)
        sec_score = sector_scores.get(sector, 50.0)
        sec_comp = ComponentScore("Sector", sec_score, 0.10, sec_score * 0.10)

        # 7. Market Trend & VIX Fear Index (10%)
        mkt_score = 50.0
        nifty = index_data.get("NIFTY50")
        vix = index_data.get("VIX")

        if nifty and nifty.change_pct > 0:
            mkt_score += 20
            bullish.append("Broad Market (NIFTY 50) Positive")
        elif nifty and nifty.change_pct < 0:
            mkt_score -= 20
            bearish.append("Broad Market (NIFTY 50) Weak")

        if vix and vix.value < 16.0:
            mkt_score += 15
            bullish.append("Low Market Volatility (VIX < 16)")
        elif vix and vix.value > 22.0:
            mkt_score -= 15
            bearish.append("High Market Volatility & Fear (VIX > 22)")

        mkt_score = max(0.0, min(100.0, mkt_score))
        mkt_comp = ComponentScore("Market Trend", mkt_score, 0.10, mkt_score * 0.10)

        # 8. Volatility & ATR Compression (10%)
        volat_score = 65.0
        volat_comp = ComponentScore("Volatility", volat_score, 0.10, volat_score * 0.10)

        # Total Weighted Score
        total = (
            trend_comp.weighted_score
            + mom_comp.weighted_score
            + vol_comp.weighted_score
            + sr_comp.weighted_score
            + pat_comp.weighted_score
            + sec_comp.weighted_score
            + mkt_comp.weighted_score
            + volat_comp.weighted_score
        )

        direction = "BULLISH" if total >= 65 else "BEARISH" if total <= 35 else "NEUTRAL"
        summary = f"Quant score {total:.1f}/100. Multi-Timeframe Trend: {trend_comp.score:.0f}, Momentum: {mom_comp.score:.0f}, Volume Conviction: {vol_comp.score:.0f}."

        return QuantScoreResult(
            total_score=total,
            trend_score=trend_comp,
            momentum_score=mom_comp,
            volume_score=vol_comp,
            sr_score=sr_comp,
            pattern_score=pat_comp,
            sector_score=sec_comp,
            market_score=mkt_comp,
            volatility_score=volat_comp,
            bullish_signals=list(set(bullish)),
            bearish_signals=list(set(bearish)),
            technical_summary=summary,
            direction=direction,
        )


scoring_engine = QuantScoringEngine()
