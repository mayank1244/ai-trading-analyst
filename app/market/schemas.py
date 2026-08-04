"""Pydantic v2 schemas for API requests and responses."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class RecommendationAction(str, Enum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    WATCHLIST = "WATCHLIST"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


class StockSchema(BaseModel):
    symbol: str
    name: str
    sector: str
    market_cap_category: str
    exchange: str = "NSE"
    is_active: bool = True


class QuoteSchema(BaseModel):
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
    market_cap: Optional[float] = None
    week_52_high: float
    week_52_low: float
    pe_ratio: Optional[float] = None
    eps: Optional[float] = None
    timestamp: datetime


class IndexDataSchema(BaseModel):
    symbol: str
    name: str
    value: float
    change: float
    change_pct: float
    timestamp: datetime


class RecommendationSchema(BaseModel):
    symbol: str
    company_name: str
    sector: str
    action: RecommendationAction
    confidence: float
    entry_price: float
    stop_loss: float
    target_1: float
    target_2: float
    risk_reward: float
    expected_holding_period: str
    quant_score: float
    ai_score: float
    overall_score: float
    bullish_signals: List[str]
    bearish_signals: List[str]
    risk_factors: List[str]
    ai_reasoning: Optional[str] = None
    news_summary: Optional[str] = None
    technical_summary: Optional[str] = None
    current_price: float
    generated_at: datetime


class ScanResultSchema(BaseModel):
    symbol: str
    name: str
    sector: str
    current_price: float
    change_pct: float
    volume: int
    quant_score: float
    recommendation: RecommendationAction
    confidence: float
    entry_price: float
    stop_loss: float
    target_1: float
    target_2: float
    risk_reward: float
    holding_period: str
    bullish_signals: List[str] = []
    bearish_signals: List[str] = []


class ChatRequestSchema(BaseModel):
    message: str
    symbol: Optional[str] = None


class ChatResponseSchema(BaseModel):
    message: str
    recommendation: Optional[dict] = None
    sources: List[str] = []
    symbol_detected: Optional[str] = None


class WatchlistSchema(BaseModel):
    symbol: str
    name: str
    added_at: datetime
    score: Optional[float] = None
    notes: Optional[str] = None
    alert_price: Optional[float] = None
