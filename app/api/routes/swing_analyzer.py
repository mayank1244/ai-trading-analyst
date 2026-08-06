"""Swing Stock Auto-Analyzer API Route (Daily Charts 3-8 Day Swing Trading)."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
import numpy as np
import pandas as pd

from app.market.data_fetcher import data_fetcher
from app.utils.logger import logger

router = APIRouter(prefix="/swing_analyzer", tags=["Swing Analyzer"])


@router.get("/analyze/{symbol}")
async def analyze_swing_stock(symbol: str) -> Dict[str, Any]:
    """Analyze a stock specifically for 3-8 Day Swing Trading on Daily Charts."""
    clean_symbol = symbol.upper().strip().replace(".NS", "").replace(".BO", "")

    try:
        # Fetch 1 year of daily OHLCV data
        ohlcv = await data_fetcher.fetch_ohlcv(clean_symbol, period="1y", interval="1d")
        if not ohlcv or ohlcv.df is None or ohlcv.df.empty or len(ohlcv.df) < 50:
            raise HTTPException(status_code=404, detail=f"Insufficient daily data for symbol '{clean_symbol}'.")

        df = ohlcv.df.copy().dropna(subset=["Close"])
        if len(df) < 50:
            raise HTTPException(status_code=400, detail="Need at least 50 daily candles for swing analysis.")

        # Fetch live real-time quote for up-to-the-minute LTP
        quote = await data_fetcher.fetch_quote(clean_symbol)
        live_ltp = quote.ltp if (quote and quote.ltp and quote.ltp > 0) else None

        # Update or append latest row with real-time live price if available
        if live_ltp:
            df.loc[df.index[-1], "Close"] = live_ltp

        closes = df["Close"].values
        highs = df["High"].values
        lows = df["Low"].values
        volumes = df["Volume"].values

        last_close = float(closes[-1])
        last_high = float(highs[-1])
        last_low = float(lows[-1])

        # 1. EMAs (20, 50, 200)
        df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()
        df["EMA_50"] = df["Close"].ewm(span=50, adjust=False).mean()
        df["EMA_200"] = df["Close"].ewm(span=min(len(df), 200), adjust=False).mean()

        ema_20_val = float(df["EMA_20"].iloc[-1])
        ema_50_val = float(df["EMA_50"].iloc[-1])
        ema_200_val = float(df["EMA_200"].iloc[-1])

        # 2. RSI (14)
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(com=13, adjust=False).mean()
        avg_loss = loss.ewm(com=13, adjust=False).mean()
        rs = avg_gain / (avg_loss + 1e-9)
        df["RSI"] = 100 - (100 / (1 + rs))
        rsi_val = float(df["RSI"].iloc[-1])

        # 3. Volume SMA 20 & Surge Ratio
        df["Vol_SMA20"] = df["Volume"].rolling(20, min_periods=5).mean()
        df["Vol_Ratio"] = df["Volume"] / (df["Vol_SMA20"] + 1e-9)

        last_vol = float(volumes[-1])
        last_vol_sma = float(df["Vol_SMA20"].iloc[-1]) if not pd.isna(df["Vol_SMA20"].iloc[-1]) else last_vol
        vol_surge_ratio = round(last_vol / max(last_vol_sma, 1.0), 2)

        # 4. 20-Day Range Check
        high_20d = float(df["High"].tail(20).max())
        low_20d = float(df["Low"].tail(20).min())

        # 5. Evaluate the 5-Point Swing Checklist
        # Rule 1: Trend Alignment (Price > EMA 20 > EMA 50)
        trend_pass = last_close > ema_20_val and ema_20_val > ema_50_val
        trend_status = "BULLISH ✅" if trend_pass else "BEARISH / WEAK ❌"

        # Rule 2: Setup Detection (EMA 20 Bounce OR Range Breakout)
        dist_to_ema20_pct = abs(last_close - ema_20_val) / last_close * 100
        is_ema20_bounce = dist_to_ema20_pct <= 3.0 and last_close >= ema_20_val
        is_breakout = last_close >= (high_20d * 0.985) and vol_surge_ratio >= 1.2

        if is_ema20_bounce and is_breakout:
            setup_name = "EMA 20 Bounce + Breakout Surge 🚀"
            setup_pass = True
        elif is_ema20_bounce:
            setup_name = "Daily 20 EMA Pullback Bounce 🎯"
            setup_pass = True
        elif is_breakout:
            setup_name = "20-Day Resistance Breakout 💥"
            setup_pass = True
        else:
            setup_name = "Consolidating / No Clear Setup ⏳"
            setup_pass = False

        # Rule 3: RSI Sweet Spot Check (48 to 65)
        rsi_pass = 48.0 <= rsi_val <= 65.0
        rsi_status = f"{rsi_val:.1f} (Sweet Spot) ✅" if rsi_pass else f"{rsi_val:.1f} (Overbought > 70 or Weak < 48) ⚠️"

        # Rule 4: Volume Surge Check (Volume Ratio >= 1.0x)
        has_recent_surge = any(v >= 1.5 for v in df["Vol_Ratio"].tail(3) if not pd.isna(v))
        vol_pass = vol_surge_ratio >= 1.0 or has_recent_surge
        vol_status = f"{vol_surge_ratio:.2f}x Avg (Strong Buying) ✅" if vol_pass else f"{vol_surge_ratio:.2f}x Avg (Low Volume) ⚠️"

        # Rule 5: Overall Swing Verdict
        score_checks = sum([trend_pass, setup_pass, rsi_pass, vol_surge_ratio >= 1.0])
        if score_checks >= 3 and trend_pass:
            verdict = "STRONG SWING BUY 🟢"
            action = "BUY"
            confidence = min(92.0, 60.0 + (score_checks * 8.0))
        elif score_checks == 2 and trend_pass:
            verdict = "WATCHLIST / WAIT 🟡"
            action = "WATCHLIST"
            confidence = 58.0
        else:
            verdict = "AVOID FOR SWING 🔴"
            action = "AVOID"
            confidence = 40.0

        # 6. Calculate Trade Plan (Entry, Stop Loss, Target 1, Target 2)
        entry_low = round(min(last_close, ema_20_val * 1.005), 2)
        entry_high = round(max(last_close, ema_20_val * 1.015), 2)
        
        # Stop loss: 2.5% below entry or below EMA 20
        stop_loss = round(min(last_close * 0.975, ema_20_val * 0.985), 2)
        risk_per_share = round(last_close - stop_loss, 2)

        # Target 1: +5%, Target 2: +8%
        target_1 = round(last_close * 1.05, 2)
        target_2 = round(last_close * 1.08, 2)
        reward_per_share = round(target_1 - last_close, 2)

        rr_ratio = round(reward_per_share / max(risk_per_share, 0.01), 2)

        # Format Daily Candles for Plotly Chart
        candles = []
        for idx, row in df.tail(120).iterrows():
            candles.append({
                "time": str(idx.date()),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"]),
                "ema_20": round(float(row["EMA_20"]), 2) if not pd.isna(row["EMA_20"]) else None,
                "ema_50": round(float(row["EMA_50"]), 2) if not pd.isna(row["EMA_50"]) else None,
                "ema_200": round(float(row["EMA_200"]), 2) if not pd.isna(row["EMA_200"]) else None,
                "rsi": round(float(row["RSI"]), 1) if not pd.isna(row["RSI"]) else None,
            })

        return {
            "symbol": clean_symbol,
            "current_price": round(last_close, 2),
            "verdict": verdict,
            "action": action,
            "confidence": round(confidence, 1),
            "setup_name": setup_name,
            "ema_20": round(ema_20_val, 2),
            "ema_50": round(ema_50_val, 2),
            "ema_200": round(ema_200_val, 2),
            "rsi": round(rsi_val, 1),
            "volume_surge_ratio": vol_surge_ratio,
            "20d_high": round(high_20d, 2),
            "20d_low": round(low_20d, 2),
            "trade_plan": {
                "entry_range": f"₹{entry_low:.2f} – ₹{entry_high:.2f}",
                "stop_loss": stop_loss,
                "target_1": target_1,
                "target_2": target_2,
                "risk_per_share": risk_per_share,
                "reward_per_share": reward_per_share,
                "risk_reward_ratio": f"1 : {rr_ratio:.1f}",
                "holding_period": "3 – 8 Trading Days",
            },
            "checklist": [
                {"name": "Trend Alignment (Price > EMA 20 > EMA 50)", "passed": trend_pass, "detail": trend_status},
                {"name": "Swing Setup (EMA 20 Bounce / Breakout)", "passed": setup_pass, "detail": setup_name},
                {"name": "RSI Sweet Spot (50 - 65 Range)", "passed": rsi_pass, "detail": rsi_status},
                {"name": "Volume Surge (Institutional Support)", "passed": vol_surge_ratio >= 1.0, "detail": vol_status},
            ],
            "candles": candles,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Swing Analyzer error for {symbol}: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))
