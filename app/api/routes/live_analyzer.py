"""Live Stock Auto-Analyzer API Route."""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
import pandas as pd
import yfinance as yf

from app.market.data_fetcher import data_fetcher
from app.technical.indicators import indicators
from app.patterns.candlestick import pattern_detector
from app.price_action.detector import price_action_detector
from app.utils.logger import logger

router = APIRouter(prefix="/live_analyzer", tags=["Live Analyzer"])

TIMEFRAME_PERIOD_MAP = {
    "1m": "1d",
    "5m": "5d",
    "15m": "1mo",
    "1h": "3mo",
    "1d": "1y",
}


@router.get("/analyze/{symbol}")
async def analyze_live_stock(
    symbol: str,
    timeframe: str = Query(default="15m", description="Timeframe: 1m, 5m, 15m, 1h, 1d"),
) -> Dict[str, Any]:
    """Fetch live OHLCV data, compute indicators, candlestick patterns, and AI signal badge."""
    symbol = symbol.upper().strip()
    if not symbol:
        raise HTTPException(status_code=400, detail="Stock symbol is required")

    interval = timeframe.lower()
    if interval not in TIMEFRAME_PERIOD_MAP:
        interval = "15m"

    period = TIMEFRAME_PERIOD_MAP[interval]

    try:
        ohlcv = await data_fetcher.fetch_ohlcv(symbol, period=period, interval=interval)
        if not ohlcv or ohlcv.df.empty:
            raise HTTPException(
                status_code=444, detail=f"No live data found for symbol '{symbol}'."
            )

        df = ohlcv.df.copy()

        # Compute Technical Indicators
        df = indicators.compute_ema(df, periods=[20, 50])
        df = indicators.compute_rsi(df, period=14)
        df = indicators.compute_macd(df, fast=12, slow=26, signal=9)
        df = indicators.compute_bollinger_bands(df, period=20, std=2)
        df = indicators.compute_vwap(df)
        df = indicators.compute_atr(df, period=14)

        # Compute Candlestick Patterns
        pattern_res = pattern_detector.detect_all(df)

        # Compute Support & Resistance + Price Action
        pa_res = price_action_detector.analyze(df)

        last_row = df.iloc[-1]
        last_close = float(last_row["Close"])
        last_open = float(last_row["Open"])
        last_high = float(last_row["High"])
        last_low = float(last_row["Low"])
        last_vol = int(last_row["Volume"])

        prev_close = float(df["Close"].iloc[-2]) if len(df) >= 2 else last_open
        change_pct = round(((last_close - prev_close) / prev_close) * 100, 2)

        ema_20 = float(last_row["EMA_20"]) if "EMA_20" in last_row and not pd.isna(last_row["EMA_20"]) else last_close
        ema_50 = float(last_row["EMA_50"]) if "EMA_50" in last_row and not pd.isna(last_row["EMA_50"]) else last_close
        rsi = float(last_row["RSI_14"]) if "RSI_14" in last_row and not pd.isna(last_row["RSI_14"]) else 50.0

        macd_val = float(last_row["MACD"]) if "MACD" in last_row and not pd.isna(last_row["MACD"]) else 0.0
        macd_sig = float(last_row["MACD_signal"]) if "MACD_signal" in last_row and not pd.isna(last_row["MACD_signal"]) else 0.0
        macd_hist = float(last_row["MACD_hist"]) if "MACD_hist" in last_row and not pd.isna(last_row["MACD_hist"]) else 0.0

        bb_lower = float(last_row["BB_lower"]) if "BB_lower" in last_row and not pd.isna(last_row["BB_lower"]) else last_close * 0.98
        bb_middle = float(last_row["BB_middle"]) if "BB_middle" in last_row and not pd.isna(last_row["BB_middle"]) else last_close
        bb_upper = float(last_row["BB_upper"]) if "BB_upper" in last_row and not pd.isna(last_row["BB_upper"]) else last_close * 1.02

        vwap_val = float(last_row["VWAP"]) if "VWAP" in last_row and not pd.isna(last_row["VWAP"]) else last_close
        atr_val = float(last_row["ATR_14"]) if "ATR_14" in last_row and not pd.isna(last_row["ATR_14"]) else (last_high - last_low)

        # Average Volume
        avg_vol_20 = int(df["Volume"].tail(20).mean()) if len(df) >= 20 else last_vol
        vol_surge_ratio = round(last_vol / max(avg_vol_20, 1), 2)

        # Signal Badge Calculation
        score = 50.0
        reasons = []

        # RSI Signal
        if rsi < 32.0:
            score += 25.0
            reasons.append(f"RSI Oversold ({rsi:.1f} < 32) — Strong Reversal Buy")
        elif rsi > 68.0:
            score -= 25.0
            reasons.append(f"RSI Overbought ({rsi:.1f} > 68) — Profit Booking Risk")
        elif 50.0 <= rsi <= 65.0:
            score += 15.0
            reasons.append(f"RSI Bullish Momentum ({rsi:.1f})")

        # MACD Crossover
        if macd_val > macd_sig:
            score += 20.0
            reasons.append("MACD Line Above Signal Line (Bullish Crossover)")
        else:
            score -= 20.0
            reasons.append("MACD Line Below Signal Line (Bearish Crossover)")

        # Price vs EMA 20 & 50
        if last_close > ema_20 and ema_20 > ema_50:
            score += 20.0
            reasons.append(f"Price (₹{last_close:.2f}) > EMA 20 (₹{ema_20:.2f}) > EMA 50 (₹{ema_50:.2f})")
        elif last_close < ema_20 and ema_20 < ema_50:
            score -= 20.0
            reasons.append(f"Price (₹{last_close:.2f}) < EMA 20 < EMA 50 (Downtrend)")

        # Volume Confirmation
        if vol_surge_ratio >= 1.5:
            score += 15.0
            reasons.append(f"Volume Surge ({vol_surge_ratio:.1f}x Above 20-candle Average)")

        # Pattern Boost
        if pattern_res and pattern_res.bullish_patterns:
            score += 10.0
            reasons.append(f"Bullish Pattern: {', '.join(pattern_res.bullish_patterns)}")
        elif pattern_res and pattern_res.bearish_patterns:
            score -= 10.0
            reasons.append(f"Bearish Pattern: {', '.join(pattern_res.bearish_patterns)}")

        score = max(0.0, min(100.0, score))

        if score >= 75:
            action = "STRONG_BUY"
        elif score >= 58:
            action = "BUY"
        elif score <= 25:
            action = "STRONG_SELL"
        elif score <= 42:
            action = "SELL"
        else:
            action = "HOLD"

        confidence = round(min(95.0, 50.0 + abs(score - 50.0) * 0.9), 1)

        # Support / Resistance Levels
        sup = pa_res.nearest_support if (pa_res and pa_res.nearest_support) else (last_close * 0.985)
        res_lvl = pa_res.nearest_resistance if (pa_res and pa_res.nearest_resistance) else (last_close * 1.015)

        sr_supports = [round(sup, 2), round(sup * 0.98, 2), round(sup * 0.96, 2)]
        sr_resistances = [round(res_lvl, 2), round(res_lvl * 1.02, 2), round(res_lvl * 1.04, 2)]

        # Risk Level
        atr_pct = (atr_val / last_close) * 100
        if atr_pct < 1.5:
            risk_level = "LOW"
        elif atr_pct < 3.0:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        # Short-term prediction
        if action in ["BUY", "STRONG_BUY"]:
            pred_dir = "BULLISH 📈"
            target_price = round(last_close + (1.8 * atr_val), 2)
            stop_loss = round(last_close - (1.2 * atr_val), 2)
            prediction = f"Likely upward trajectory toward ₹{target_price:.2f} (+{round(((target_price - last_close)/last_close)*100, 2)}%) over next 3-5 candles."
        elif action in ["SELL", "STRONG_SELL"]:
            pred_dir = "BEARISH 📉"
            target_price = round(last_close - (1.8 * atr_val), 2)
            stop_loss = round(last_close + (1.2 * atr_val), 2)
            prediction = f"Likely downward pressure toward ₹{target_price:.2f} ({round(((target_price - last_close)/last_close)*100, 2)}%) over next 3-5 candles."
        else:
            pred_dir = "SIDEWAYS ➡️"
            target_price = round(last_close * 1.01, 2)
            stop_loss = round(last_close * 0.99, 2)
            prediction = f"Consolidating within ₹{stop_loss:.2f} – ₹{target_price:.2f} range."

        # Candle Data for Plotly Chart
        chart_candles = []
        for idx, row in df.iterrows():
            candle_time = idx.strftime("%Y-%m-%d %H:%M") if hasattr(idx, "strftime") else str(idx)
            chart_candles.append({
                "time": candle_time,
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"]),
                "ema_20": round(float(row["EMA_20"]), 2) if "EMA_20" in row and not pd.isna(row["EMA_20"]) else None,
                "ema_50": round(float(row["EMA_50"]), 2) if "EMA_50" in row and not pd.isna(row["EMA_50"]) else None,
                "rsi": round(float(row["RSI_14"]), 2) if "RSI_14" in row and not pd.isna(row["RSI_14"]) else None,
                "macd": round(float(row["MACD"]), 2) if "MACD" in row and not pd.isna(row["MACD"]) else None,
                "macd_sig": round(float(row["MACD_signal"]), 2) if "MACD_signal" in row and not pd.isna(row["MACD_signal"]) else None,
                "macd_hist": round(float(row["MACD_hist"]), 2) if "MACD_hist" in row and not pd.isna(row["MACD_hist"]) else None,
                "bb_upper": round(float(row["BB_upper"]), 2) if "BB_upper" in row and not pd.isna(row["BB_upper"]) else None,
                "bb_middle": round(float(row["BB_middle"]), 2) if "BB_middle" in row and not pd.isna(row["BB_middle"]) else None,
                "bb_lower": round(float(row["BB_lower"]), 2) if "BB_lower" in row and not pd.isna(row["BB_lower"]) else None,
                "vwap": round(float(row["VWAP"]), 2) if "VWAP" in row and not pd.isna(row["VWAP"]) else None,
            })

        detected_pattern_names = [p.name for p in pattern_res.detected_patterns] if pattern_res else []

        return {
            "symbol": symbol,
            "timeframe": interval,
            "current_price": last_close,
            "change_pct": change_pct,
            "volume": last_vol,
            "volume_surge_ratio": vol_surge_ratio,
            "action": action,
            "score": round(score, 1),
            "confidence": confidence,
            "reasons": reasons,
            "ema_20": round(ema_20, 2),
            "ema_50": round(ema_50, 2),
            "rsi": round(rsi, 1),
            "macd": round(macd_val, 2),
            "macd_signal": round(macd_sig, 2),
            "macd_hist": round(macd_hist, 2),
            "bb_lower": round(bb_lower, 2),
            "bb_middle": round(bb_middle, 2),
            "bb_upper": round(bb_upper, 2),
            "vwap": round(vwap_val, 2),
            "atr": round(atr_val, 2),
            "trend_direction": pa_res.trend if pa_res else ("UPTREND" if last_close > ema_20 else "DOWNTREND"),
            "support_levels": sr_supports,
            "resistance_levels": sr_resistances,
            "detected_patterns": detected_pattern_names,
            "bullish_patterns": pattern_res.bullish_patterns if pattern_res else [],
            "bearish_patterns": pattern_res.bearish_patterns if pattern_res else [],
            "prediction": prediction,
            "prediction_direction": pred_dir,
            "target_price": target_price,
            "stop_loss": stop_loss,
            "risk_level": risk_level,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "candles": chart_candles,
        }

    except Exception as exc:
        logger.error("Live Stock Auto-Analyzer error for {}: {}", symbol, exc)
        raise HTTPException(status_code=500, detail=str(exc))
