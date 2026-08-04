"""Technical Indicators Engine using pandas-ta."""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import numpy as np
import pandas as pd
import pandas_ta as ta

from app.utils.logger import logger


@dataclass
class IndicatorResult:
    name: str
    value: float
    signal: str  # BULLISH, BEARISH, NEUTRAL
    detail: str
    strength: float  # 0-100


class TechnicalIndicators:
    def compute_ema(self, df: pd.DataFrame, periods=[9, 21, 50, 200]) -> pd.DataFrame:
        df = df.copy()
        for p in periods:
            df[f"EMA_{p}"] = ta.ema(df["Close"], length=p)
        return df

    def compute_sma(self, df: pd.DataFrame, periods=[20, 50, 100, 200]) -> pd.DataFrame:
        df = df.copy()
        for p in periods:
            df[f"SMA_{p}"] = ta.sma(df["Close"], length=p)
        return df

    def compute_rsi(self, df: pd.DataFrame, period=14) -> pd.DataFrame:
        df = df.copy()
        df[f"RSI_{period}"] = ta.rsi(df["Close"], length=period)
        return df

    def compute_macd(self, df: pd.DataFrame, fast=12, slow=26, signal=9) -> pd.DataFrame:
        df = df.copy()
        macd = ta.macd(df["Close"], fast=fast, slow=slow, signal=signal)
        if macd is not None and not macd.empty:
            df["MACD"] = macd.iloc[:, 0]
            df["MACD_hist"] = macd.iloc[:, 1]
            df["MACD_signal"] = macd.iloc[:, 2]
        return df

    def compute_vwap(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        try:
            vwap = ta.vwap(df["High"], df["Low"], df["Close"], df["Volume"])
            df["VWAP"] = vwap if vwap is not None else (df["High"] + df["Low"] + df["Close"]) / 3
        except Exception:
            df["VWAP"] = (df["High"] + df["Low"] + df["Close"]) / 3
        return df

    def compute_atr(self, df: pd.DataFrame, period=14) -> pd.DataFrame:
        df = df.copy()
        df[f"ATR_{period}"] = ta.atr(df["High"], df["Low"], df["Close"], length=period)
        return df

    def compute_adx(self, df: pd.DataFrame, period=14) -> pd.DataFrame:
        df = df.copy()
        adx = ta.adx(df["High"], df["Low"], df["Close"], length=period)
        if adx is not None and not adx.empty:
            df[f"ADX_{period}"] = adx.iloc[:, 0]
            df["DI_plus"] = adx.iloc[:, 1]
            df["DI_minus"] = adx.iloc[:, 2]
        return df

    def compute_supertrend(self, df: pd.DataFrame, period=7, multiplier=3) -> pd.DataFrame:
        df = df.copy()
        st = ta.supertrend(df["High"], df["Low"], df["Close"], length=period, multiplier=multiplier)
        if st is not None and not st.empty:
            df["Supertrend"] = st.iloc[:, 0]
            df["Supertrend_direction"] = st.iloc[:, 1]  # 1 for bullish, -1 for bearish
        return df

    def compute_bollinger_bands(self, df: pd.DataFrame, period=20, std=2) -> pd.DataFrame:
        df = df.copy()
        bb = ta.bbands(df["Close"], length=period, std=std)
        if bb is not None and not bb.empty:
            df["BB_lower"] = bb.iloc[:, 0]
            df["BB_middle"] = bb.iloc[:, 1]
            df["BB_upper"] = bb.iloc[:, 2]
            df["BB_width"] = (df["BB_upper"] - df["BB_lower"]) / df["BB_middle"]
        return df

    def compute_stochastic_rsi(
        self, df: pd.DataFrame, period=14, smooth_k=3, smooth_d=3
    ) -> pd.DataFrame:
        df = df.copy()
        stoch = ta.stochrsi(df["Close"], length=period, rsi_length=period, k=smooth_k, d=smooth_d)
        if stoch is not None and not stoch.empty:
            df["StochRSI_K"] = stoch.iloc[:, 0]
            df["StochRSI_D"] = stoch.iloc[:, 1]
        return df

    def compute_obv(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["OBV"] = ta.obv(df["Close"], df["Volume"])
        return df

    def compute_cci(self, df: pd.DataFrame, period=20) -> pd.DataFrame:
        df = df.copy()
        df[f"CCI_{period}"] = ta.cci(df["High"], df["Low"], df["Close"], length=period)
        return df

    def compute_all(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, IndicatorResult]]:
        df = self.compute_ema(df)
        df = self.compute_sma(df)
        df = self.compute_rsi(df)
        df = self.compute_macd(df)
        df = self.compute_vwap(df)
        df = self.compute_atr(df)
        df = self.compute_adx(df)
        df = self.compute_supertrend(df)
        df = self.compute_bollinger_bands(df)
        df = self.compute_stochastic_rsi(df)
        df = self.compute_obv(df)
        df = self.compute_cci(df)

        last = df.iloc[-1]
        results = {}

        # RSI evaluation
        rsi_val = float(last.get("RSI_14", 50))
        if rsi_val > 60:
            rsi_sig = IndicatorResult("RSI (14)", rsi_val, "BULLISH", f"RSI is bullish at {rsi_val:.1f}", 75)
        elif rsi_val < 40:
            rsi_sig = IndicatorResult("RSI (14)", rsi_val, "BEARISH", f"RSI is bearish at {rsi_val:.1f}", 75)
        else:
            rsi_sig = IndicatorResult("RSI (14)", rsi_val, "NEUTRAL", f"RSI is neutral at {rsi_val:.1f}", 50)
        results["RSI"] = rsi_sig

        # MACD evaluation
        macd = float(last.get("MACD", 0))
        signal = float(last.get("MACD_signal", 0))
        if macd > signal:
            macd_sig = IndicatorResult("MACD", macd, "BULLISH", "MACD line is above signal line", 80)
        else:
            macd_sig = IndicatorResult("MACD", macd, "BEARISH", "MACD line is below signal line", 80)
        results["MACD"] = macd_sig

        # EMA evaluation
        close = float(last["Close"])
        ema_50 = float(last.get("EMA_50", close))
        ema_200 = float(last.get("EMA_200", close))
        if close > ema_50 > ema_200:
            ema_sig = IndicatorResult("EMA Alignment", close, "BULLISH", "Price is above 50 & 200 EMA", 90)
        elif close < ema_50 < ema_200:
            ema_sig = IndicatorResult("EMA Alignment", close, "BEARISH", "Price is below 50 & 200 EMA", 90)
        else:
            ema_sig = IndicatorResult("EMA Alignment", close, "NEUTRAL", "Mixed EMA signals", 50)
        results["EMA"] = ema_sig

        # Supertrend evaluation
        st_dir = float(last.get("Supertrend_direction", 0))
        if st_dir == 1:
            st_sig = IndicatorResult("Supertrend", float(last.get("Supertrend", close)), "BULLISH", "Supertrend is Bullish", 85)
        elif st_dir == -1:
            st_sig = IndicatorResult("Supertrend", float(last.get("Supertrend", close)), "BEARISH", "Supertrend is Bearish", 85)
        else:
            st_sig = IndicatorResult("Supertrend", close, "NEUTRAL", "Supertrend Neutral", 50)
        results["Supertrend"] = st_sig

        return df, results


indicators = TechnicalIndicators()
