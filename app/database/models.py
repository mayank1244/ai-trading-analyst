"""SQLAlchemy ORM models for the AI Trading Analyst application."""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass


class Stock(Base):
    __tablename__ = "stocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sector: Mapped[str] = mapped_column(String(100), nullable=False)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    market_cap_category: Mapped[str] = mapped_column(
        String(10), nullable=False, default="large"
    )
    exchange: Mapped[str] = mapped_column(String(10), nullable=False, default="NSE")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    prices: Mapped[list[StockPrice]] = relationship(
        "StockPrice", back_populates="stock", cascade="all, delete-orphan"
    )
    recommendations: Mapped[list[Recommendation]] = relationship(
        "Recommendation", back_populates="stock", cascade="all, delete-orphan"
    )
    news: Mapped[list[NewsArticle]] = relationship(
        "NewsArticle", back_populates="stock", cascade="all, delete-orphan"
    )


class StockPrice(Base):
    __tablename__ = "stock_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[int] = mapped_column(Integer, nullable=False)
    vwap: Mapped[float | None] = mapped_column(Float, nullable=True)
    interval: Mapped[str] = mapped_column(String(10), nullable=False, default="1d")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    stock: Mapped[Stock] = relationship("Stock", back_populates="prices")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    stop_loss: Mapped[float] = mapped_column(Float, nullable=False)
    target_1: Mapped[float] = mapped_column(Float, nullable=False)
    target_2: Mapped[float] = mapped_column(Float, nullable=False)
    risk_reward: Mapped[float] = mapped_column(Float, nullable=False)
    holding_period: Mapped[str] = mapped_column(String(50), nullable=False)

    quant_score: Mapped[float] = mapped_column(Float, nullable=False)
    ai_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    trend_score: Mapped[float] = mapped_column(Float, nullable=False)
    momentum_score: Mapped[float] = mapped_column(Float, nullable=False)
    volume_score: Mapped[float] = mapped_column(Float, nullable=False)
    sr_score: Mapped[float] = mapped_column(Float, nullable=False)
    pattern_score: Mapped[float] = mapped_column(Float, nullable=False)
    sector_score: Mapped[float] = mapped_column(Float, nullable=False)
    market_score: Mapped[float] = mapped_column(Float, nullable=False)
    volatility_score: Mapped[float] = mapped_column(Float, nullable=False)

    bullish_signals: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    bearish_signals: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    risk_factors: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    ai_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    news_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    technical_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    current_price: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    stock: Mapped[Stock] = relationship("Stock", back_populates="recommendations")
    backtest_records: Mapped[list[BacktestRecord]] = relationship(
        "BacktestRecord", back_populates="recommendation", cascade="all, delete-orphan"
    )


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stock_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("stocks.id", ondelete="SET NULL"), nullable=True, index=True
    )
    symbol: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    sentiment: Mapped[str] = mapped_column(
        String(10), nullable=False, default="neutral"
    )
    sentiment_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_processed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    stock: Mapped[Stock | None] = relationship("Stock", back_populates="news")


class Watchlist(Base):
    __tablename__ = "watchlist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    watchlist_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    holding_period: Mapped[str | None] = mapped_column(String(50), nullable=True)
    added_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    alert_price: Mapped[float | None] = mapped_column(Float, nullable=True)


class BacktestRecord(Base):
    __tablename__ = "backtest_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recommendation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("recommendations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    entry_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    exit_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    exit_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    actual_return_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    hit_target_1: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    hit_target_2: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    hit_stop_loss: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    holding_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(
        String(10), nullable=False, default="OPEN"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    recommendation: Mapped[Recommendation] = relationship(
        "Recommendation", back_populates="backtest_records"
    )


class SectorAnalysis(Base):
    __tablename__ = "sector_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sector: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    momentum: Mapped[str] = mapped_column(
        String(10), nullable=False, default="neutral"
    )
    top_stocks: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    avg_return_1d: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_return_5d: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_return_30d: Mapped[float | None] = mapped_column(Float, nullable=True)
    analysis_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
