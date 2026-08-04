"""AI Reasoning Engine (30% component)."""

from dataclasses import dataclass, field
from typing import List, Optional
import json
from openai import AsyncOpenAI

from app.config.settings import settings
from app.utils.logger import logger


@dataclass
class AIAnalysis:
    ai_score: float
    setup_explanation: str
    strengths: List[str]
    weaknesses: List[str]
    news_summary: str
    hidden_risks: List[str]
    confidence_adjustment: float
    holding_advice: str
    risk_warning: str
    model_used: str = "gpt-4o-mini"


class AIReasoningEngine:
    async def analyze(
        self,
        symbol: str,
        company_name: str,
        sector: str,
        quant_res,
        current_price: float,
        risk_params,
        news_articles: List = [],
        sentiment_res = None,
    ) -> AIAnalysis:
        if not settings.OPENAI_API_KEY:
            # Fallback when OpenAI key is not set
            return AIAnalysis(
                ai_score=quant_res.total_score,
                setup_explanation=f"Quantitative analysis setup for {symbol} ({company_name}) in {sector} sector.",
                strengths=quant_res.bullish_signals,
                weaknesses=quant_res.bearish_signals,
                news_summary=sentiment_res.summary if sentiment_res else "No news available.",
                hidden_risks=["Market volatility", "Sector sentiment shifts"],
                confidence_adjustment=0.0,
                holding_advice=f"Expected holding period: {risk_params.holding_period}",
                risk_warning=f"Strict stop loss at ₹{risk_params.stop_loss:.2f}",
                model_used="rule-based-fallback",
            )

        try:
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            prompt = f"""
Analyze stock: {symbol} ({company_name})
Sector: {sector}
Current Price: ₹{current_price}
Quant Score: {quant_res.total_score:.1f}/100
Technical Summary: {quant_res.technical_summary}
Bullish Signals: {', '.join(quant_res.bullish_signals)}
Bearish Signals: {', '.join(quant_res.bearish_signals)}
Risk Params: Entry ₹{risk_params.entry_price}, SL ₹{risk_params.stop_loss}, T1 ₹{risk_params.target_1}, T2 ₹{risk_params.target_2}
News Summary: {sentiment_res.summary if sentiment_res else 'N/A'}

Provide reasoning as JSON:
{{
  "ai_score": float (0-100),
  "setup_explanation": "str",
  "strengths": ["str"],
  "weaknesses": ["str"],
  "news_summary": "str",
  "hidden_risks": ["str"],
  "confidence_adjustment": float (-10 to +10),
  "holding_advice": "str",
  "risk_warning": "str"
}}
"""
            resp = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a quantitative market analyst for Indian stock markets."},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=0.3,
            )

            data = json.loads(resp.choices[0].message.content)
            return AIAnalysis(
                ai_score=float(data.get("ai_score", quant_res.total_score)),
                setup_explanation=data.get("setup_explanation", ""),
                strengths=data.get("strengths", []),
                weaknesses=data.get("weaknesses", []),
                news_summary=data.get("news_summary", ""),
                hidden_risks=data.get("hidden_risks", []),
                confidence_adjustment=float(data.get("confidence_adjustment", 0.0)),
                holding_advice=data.get("holding_advice", ""),
                risk_warning=data.get("risk_warning", ""),
                model_used=settings.OPENAI_MODEL,
            )
        except Exception as exc:
            logger.error("AI reasoning error for {}: {}", symbol, exc)
            return AIAnalysis(
                ai_score=quant_res.total_score,
                setup_explanation=f"Analysis for {symbol}.",
                strengths=quant_res.bullish_signals,
                weaknesses=quant_res.bearish_signals,
                news_summary="N/A",
                hidden_risks=[],
                confidence_adjustment=0.0,
                holding_advice="",
                risk_warning="",
            )


ai_engine = AIReasoningEngine()
