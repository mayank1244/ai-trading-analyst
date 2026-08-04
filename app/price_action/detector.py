"""Price Action Analysis Module."""

from dataclasses import dataclass
from typing import List, Optional, Tuple
import numpy as np
import pandas as pd

from app.utils.logger import logger


@dataclass
class SupportResistanceLevel:
    price: float
    strength: int
    level_type: str  # SUPPORT or RESISTANCE


@dataclass
class PriceActionResult:
    trend: str  # UPTREND, DOWNTREND, SIDEWAYS
    trend_strength: str  # STRONG, MODERATE, WEAK
    is_breakout: bool
    is_breakdown: bool
    is_gap_up: bool
    is_gap_down: bool
    has_higher_highs: bool
    has_higher_lows: bool
    is_near_support: bool
    is_near_resistance: bool
    nearest_support: Optional[float]
    nearest_resistance: Optional[float]
    swing_high: float
    swing_low: float
    price_action_score: float
    bullish_signals: List[str]
    bearish_signals: List[str]


class PriceActionDetector:
    def detect_trend(self, df: pd.DataFrame) -> Tuple[str, str]:
        closes = df["Close"].values
        if len(closes) < 20:
            return "SIDEWAYS", "WEAK"

        sma_20 = pd.Series(closes).rolling(20).mean().iloc[-1]
        sma_50 = pd.Series(closes).rolling(50).mean().iloc[-1] if len(closes) >= 50 else sma_20

        current = closes[-1]
        if current > sma_20 > sma_50:
            return "UPTREND", "STRONG"
        elif current > sma_20:
            return "UPTREND", "MODERATE"
        elif current < sma_20 < sma_50:
            return "DOWNTREND", "STRONG"
        elif current < sma_20:
            return "DOWNTREND", "MODERATE"
        return "SIDEWAYS", "WEAK"

    def find_support_resistance(
        self, df: pd.DataFrame
    ) -> Tuple[List[SupportResistanceLevel], List[SupportResistanceLevel]]:
        highs = df["High"].tail(100).values
        lows = df["Low"].tail(100).values
        current = df["Close"].iloc[-1]

        supports = []
        resistances = []

        # Quantile-based clustering for key levels
        for val in np.quantile(lows, [0.1, 0.25]):
            if val < current:
                supports.append(SupportResistanceLevel(float(val), 2, "SUPPORT"))

        for val in np.quantile(highs, [0.75, 0.9]):
            if val > current:
                resistances.append(SupportResistanceLevel(float(val), 2, "RESISTANCE"))

        return supports, resistances

    def analyze(self, df: pd.DataFrame) -> PriceActionResult:
        trend, trend_strength = self.detect_trend(df)
        supports, resistances = self.find_support_resistance(df)

        current = df["Close"].iloc[-1]
        prev_close = df["Close"].iloc[-2] if len(df) > 1 else current
        open_price = df["Open"].iloc[-1]

        # Gap detection
        is_gap_up = open_price > prev_close * 1.01
        is_gap_down = open_price < prev_close * 0.99

        # Breakout / Breakdown
        recent_high = df["High"].tail(20).iloc[:-1].max()
        recent_low = df["Low"].tail(20).iloc[:-1].min()

        is_breakout = current > recent_high
        is_breakdown = current < recent_low

        # HH & HL
        highs_tail = df["High"].tail(10).values
        lows_tail = df["Low"].tail(10).values
        has_higher_highs = highs_tail[-1] > highs_tail[-5]
        has_higher_lows = lows_tail[-1] > lows_tail[-5]

        nearest_supp = supports[0].price if supports else recent_low
        nearest_res = resistances[0].price if resistances else recent_high

        is_near_support = abs(current - nearest_supp) / current < 0.02
        is_near_resistance = abs(current - nearest_res) / current < 0.02

        bullish_signals = []
        bearish_signals = []

        score = 50.0
        if trend == "UPTREND":
            score += 20
            bullish_signals.append("Price is in Uptrend")
        elif trend == "DOWNTREND":
            score -= 20
            bearish_signals.append("Price is in Downtrend")

        if is_breakout:
            score += 20
            bullish_signals.append("Bullish Breakout over 20-day high")
        if is_breakdown:
            score -= 20
            bearish_signals.append("Bearish Breakdown below 20-day low")

        if is_near_support:
            score += 10
            bullish_signals.append("Price near Support level")
        if is_near_resistance:
            score -= 10
            bearish_signals.append("Price near Resistance level")

        score = float(max(0.0, min(100.0, score)))

        return PriceActionResult(
            trend=trend,
            trend_strength=trend_strength,
            is_breakout=is_breakout,
            is_breakdown=is_breakdown,
            is_gap_up=is_gap_up,
            is_gap_down=is_gap_down,
            has_higher_highs=has_higher_highs,
            has_higher_lows=has_higher_lows,
            is_near_support=is_near_support,
            is_near_resistance=is_near_resistance,
            nearest_support=nearest_supp,
            nearest_resistance=nearest_res,
            swing_high=float(recent_high),
            swing_low=float(recent_low),
            price_action_score=score,
            bullish_signals=bullish_signals,
            bearish_signals=bearish_signals,
        )


price_action_detector = PriceActionDetector()
