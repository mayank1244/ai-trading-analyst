"""Candlestick Pattern Recognition Engine."""

from dataclasses import dataclass, field
from typing import List, Optional
import pandas as pd


@dataclass
class CandlestickPattern:
    name: str
    pattern_type: str  # BULLISH, BEARISH, NEUTRAL
    confidence: float
    description: str


@dataclass
class PatternResult:
    detected_patterns: List[CandlestickPattern] = field(default_factory=list)
    bullish_patterns: List[str] = field(default_factory=list)
    bearish_patterns: List[str] = field(default_factory=list)
    dominant_signal: str = "NEUTRAL"
    pattern_score: float = 50.0


class CandlestickDetector:
    def detect_hammer(self, df: pd.DataFrame) -> Optional[CandlestickPattern]:
        if len(df) < 2:
            return None
        row = df.iloc[-1]
        body = abs(row["Close"] - row["Open"])
        candle_range = row["High"] - row["Low"]
        lower_shadow = min(row["Open"], row["Close"]) - row["Low"]
        upper_shadow = row["High"] - max(row["Open"], row["Close"])

        if candle_range > 0 and lower_shadow >= 2 * body and upper_shadow <= 0.2 * body:
            return CandlestickPattern("Hammer", "BULLISH", 80.0, "Bullish reversal pattern detected")
        return None

    def detect_shooting_star(self, df: pd.DataFrame) -> Optional[CandlestickPattern]:
        if len(df) < 2:
            return None
        row = df.iloc[-1]
        body = abs(row["Close"] - row["Open"])
        candle_range = row["High"] - row["Low"]
        upper_shadow = row["High"] - max(row["Open"], row["Close"])
        lower_shadow = min(row["Open"], row["Close"]) - row["Low"]

        if candle_range > 0 and upper_shadow >= 2 * body and lower_shadow <= 0.2 * body:
            return CandlestickPattern("Shooting Star", "BEARISH", 80.0, "Bearish reversal pattern detected")
        return None

    def detect_engulfing(self, df: pd.DataFrame) -> Optional[CandlestickPattern]:
        if len(df) < 2:
            return None
        prev = df.iloc[-2]
        curr = df.iloc[-1]

        # Bullish Engulfing
        if prev["Close"] < prev["Open"] and curr["Close"] > curr["Open"]:
            if curr["Open"] <= prev["Close"] and curr["Close"] >= prev["Open"]:
                return CandlestickPattern("Bullish Engulfing", "BULLISH", 85.0, "Strong bullish engulfing pattern")

        # Bearish Engulfing
        if prev["Close"] > prev["Open"] and curr["Close"] < curr["Open"]:
            if curr["Open"] >= prev["Close"] and curr["Close"] <= prev["Open"]:
                return CandlestickPattern("Bearish Engulfing", "BEARISH", 85.0, "Strong bearish engulfing pattern")

        return None

    def detect_doji(self, df: pd.DataFrame) -> Optional[CandlestickPattern]:
        if len(df) < 1:
            return None
        row = df.iloc[-1]
        body = abs(row["Close"] - row["Open"])
        candle_range = row["High"] - row["Low"]

        if candle_range > 0 and body / candle_range < 0.1:
            return CandlestickPattern("Doji", "NEUTRAL", 60.0, "Indecision Doji pattern detected")
        return None

    def detect_all(self, df: pd.DataFrame) -> PatternResult:
        patterns = []
        h = self.detect_hammer(df)
        if h: patterns.append(h)
        ss = self.detect_shooting_star(df)
        if ss: patterns.append(ss)
        eng = self.detect_engulfing(df)
        if eng: patterns.append(eng)
        dj = self.detect_doji(df)
        if dj: patterns.append(dj)

        bullish = [p.name for p in patterns if p.pattern_type == "BULLISH"]
        bearish = [p.name for p in patterns if p.pattern_type == "BEARISH"]

        score = 50.0 + len(bullish) * 15.0 - len(bearish) * 15.0
        score = float(max(0.0, min(100.0, score)))

        dom = "BULLISH" if len(bullish) > len(bearish) else "BEARISH" if len(bearish) > len(bullish) else "NEUTRAL"

        return PatternResult(
            detected_patterns=patterns,
            bullish_patterns=bullish,
            bearish_patterns=bearish,
            dominant_signal=dom,
            pattern_score=score,
        )


pattern_detector = CandlestickDetector()
