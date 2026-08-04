"""Recommendation Engine: Combines 70% Quant + 30% AI."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from app.ai.reasoning import ai_engine
from app.market.data_fetcher import data_fetcher
from app.market.nse_universe import NSE_UNIVERSE
from app.news.fetcher import news_fetcher
from app.patterns.candlestick import pattern_detector
from app.price_action.detector import price_action_detector
from app.risk.calculator import risk_calculator
from app.sentiment.analyzer import sentiment_analyzer
from app.strategy.scoring import scoring_engine
from app.technical.indicators import indicators
from app.utils.logger import logger


@dataclass
class FinalRecommendation:
    symbol: str
    company_name: str
    sector: str
    exchange: str = "NSE"
    current_price: float = 0.0
    change_pct: float = 0.0

    action: str = "HOLD"
    confidence: float = 0.0

    entry_price: float = 0.0
    stop_loss: float = 0.0
    target_1: float = 0.0
    target_2: float = 0.0
    risk_reward: float = 0.0
    expected_holding_period: str = ""

    quant_score: float = 0.0
    ai_score: float = 50.0
    overall_score: float = 0.0

    trend_score: float = 0.0
    momentum_score: float = 0.0
    volume_score: float = 0.0
    sr_score: float = 0.0
    pattern_score: float = 0.0
    sector_score: float = 0.0
    market_score: float = 0.0
    volatility_score: float = 0.0

    bullish_signals: List[str] = field(default_factory=list)
    bearish_signals: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)

    ai_reasoning: str = ""
    news_summary: str = ""
    technical_summary: str = ""
    sector_analysis: str = ""
    detailed_explanation: str = ""

    generated_at: datetime = field(default_factory=datetime.now)


class RecommendationEngine:
    async def analyze_stock(
        self, symbol: str, skip_ai: bool = False
    ) -> Optional[FinalRecommendation]:
        try:
            ohlcv = await data_fetcher.fetch_ohlcv(symbol, period="1y", interval="1d")
            if ohlcv is None or len(ohlcv.df) < 30:
                return None

            df, ind_res = indicators.compute_all(ohlcv.df)
            pa_res = price_action_detector.analyze(df)
            pat_res = pattern_detector.detect_all(df)

            stock_info = NSE_UNIVERSE.get(symbol)
            sector = stock_info.sector if stock_info else "General"
            company_name = stock_info.name if stock_info else symbol

            index_data = await data_fetcher.fetch_index_data()

            quant_res = scoring_engine.compute(
                df, ind_res, pa_res, pat_res, sector, {}, index_data
            )

            # Determine baseline quant action
            action_label = "HOLD"
            if quant_res.total_score >= 80:
                action_label = "STRONG_BUY"
            elif quant_res.total_score >= 65:
                action_label = "BUY"
            elif quant_res.total_score >= 50:
                action_label = "WATCHLIST"
            elif quant_res.total_score <= 35:
                action_label = "SELL"

            # Fetch live quote for exact Last Traded Price (LTP)
            quote = await data_fetcher.fetch_quote(symbol)
            if quote and quote.ltp > 0:
                current_price = quote.ltp
                chg_pct = quote.change_pct
            else:
                current_price = float(df["Close"].iloc[-1])
                prev_close = float(df["Close"].iloc[-2]) if len(df) > 1 else current_price
                chg_pct = (current_price - prev_close) / prev_close * 100

            risk_res = risk_calculator.compute(df, action_label, current_price=current_price)
            news_articles = await news_fetcher.fetch_stock_news(symbol)
            sentiment_res = sentiment_analyzer.analyze_articles(news_articles)

            if skip_ai:
                ai_score = quant_res.total_score
                ai_reason = "AI Reasoning skipped (Quick Mode)."
            else:
                ai_res = await ai_engine.analyze(
                    symbol, company_name, sector, quant_res, current_price, risk_res, news_articles, sentiment_res
                )
                ai_score = ai_res.ai_score
                ai_reason = ai_res.setup_explanation

            # Hybrid Decision Engine: 70% Quant + 30% AI
            overall = 0.70 * quant_res.total_score + 0.30 * ai_score
            confidence = overall

            final_action = "HOLD"
            if quant_res.total_score <= 35:
                final_action = "SELL"
            elif confidence >= 85:
                final_action = "STRONG_BUY"
            elif confidence >= 70:
                final_action = "BUY"
            elif confidence >= 55:
                final_action = "WATCHLIST"

            explanation = (
                f"### {symbol} Analysis Summary\n"
                f"**Recommendation:** {final_action} (Confidence: {confidence:.1f}%)\n"
                f"**Hybrid Score:** Quant 70% ({quant_res.total_score:.1f}) + AI 30% ({ai_score:.1f}) = {overall:.1f}\n\n"
                f"**Trade Setup:**\n"
                f"- Live LTP: ₹{current_price:,.2f}\n"
                f"- Entry: ₹{risk_res.entry_price:.2f}\n"
                f"- Stop Loss: ₹{risk_res.stop_loss:.2f} ({risk_res.stop_loss_pct:.1f}%)\n"
                f"- Target 1: ₹{risk_res.target_1:.2f} (+{risk_res.target_1_pct:.1f}%)\n"
                f"- Target 2: ₹{risk_res.target_2:.2f} (+{risk_res.target_2_pct:.1f}%)\n"
                f"- Risk:Reward: 1:{risk_res.risk_reward_1:.1f}\n"
                f"- Holding Period: {risk_res.holding_period}\n\n"
                f"**Technical Summary:**\n{quant_res.technical_summary}\n\n"
                f"**AI Reasoning:**\n{ai_reason}"
            )

            return FinalRecommendation(
                symbol=symbol,
                company_name=company_name,
                sector=sector,
                current_price=current_price,
                change_pct=round(chg_pct, 2),
                action=final_action,
                confidence=round(confidence, 1),
                entry_price=risk_res.entry_price,
                stop_loss=risk_res.stop_loss,
                target_1=risk_res.target_1,
                target_2=risk_res.target_2,
                risk_reward=risk_res.risk_reward_1,
                expected_holding_period=risk_res.holding_period,
                quant_score=round(quant_res.total_score, 1),
                ai_score=round(ai_score, 1),
                overall_score=round(overall, 1),
                trend_score=round(quant_res.trend_score.score, 1),
                momentum_score=round(quant_res.momentum_score.score, 1),
                volume_score=round(quant_res.volume_score.score, 1),
                sr_score=round(quant_res.sr_score.score, 1),
                pattern_score=round(quant_res.pattern_score.score, 1),
                sector_score=round(quant_res.sector_score.score, 1),
                market_score=round(quant_res.market_score.score, 1),
                volatility_score=round(quant_res.volatility_score.score, 1),
                bullish_signals=quant_res.bullish_signals,
                bearish_signals=quant_res.bearish_signals,
                risk_factors=[f"Stop Loss at ₹{risk_res.stop_loss}"],
                ai_reasoning=ai_reason,
                news_summary=sentiment_res.summary if sentiment_res else "",
                technical_summary=quant_res.technical_summary,
                sector_analysis=f"{sector} sector strength: {quant_res.sector_score.score:.0f}/100",
                detailed_explanation=explanation,
            )
        except Exception as exc:
            logger.error("Error generating recommendation for {}: {}", symbol, exc)
            return None


recommendation_engine = RecommendationEngine()
