"""Chat Assistant API Routes."""

from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
from openai import AsyncOpenAI

from app.config.settings import settings
from app.ranking.engine import recommendation_engine
from app.utils.logger import logger

router = APIRouter(prefix="/chat", tags=["Chat Assistant"])


class ChatRequest(BaseModel):
    message: str
    symbol: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
    recommendation: Optional[dict] = None
    sources: list = []


@router.post("")
async def chat_assistant(req: ChatRequest):
    sym = req.symbol
    rec_dict = None

    if sym:
        rec = await recommendation_engine.analyze_stock(sym.upper(), skip_ai=True)
        if rec:
            rec_dict = rec.__dict__

    if settings.OPENAI_API_KEY:
        try:
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            sys_msg = (
                "You are an expert Indian stock market analyst. "
                "Provide helpful quantitative advice for NSE/BSE stocks. "
                "Use ₹ for prices and always emphasize risk management."
            )
            context = f"User is asking about {sym}. Live rec: {rec_dict}" if rec_dict else ""
            resp = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": f"{context}\n\nUser Question: {req.message}"},
                ],
                max_tokens=800,
            )
            msg = resp.choices[0].message.content
        except Exception as exc:
            logger.error("Chat error: {}", exc)
            msg = f"I am your AI Trading Analyst. Regarding '{req.message}': Please run the technical scanner or select a specific stock for analysis."
    else:
        msg = f"I am your AI Trading Assistant. To analyze a stock, please type its symbol or use the Stock Analysis tab."
        if rec_dict:
            msg += f"\n\nAnalysis for {sym}: Recommendation is {rec_dict.get('action')} with {rec_dict.get('confidence')}% confidence."

    return ChatResponse(message=msg, recommendation=rec_dict, sources=["NSE Technical Engine"])
