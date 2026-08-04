"""News fetcher module using yfinance and fallback scraping."""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import yfinance as yf

from app.utils.logger import logger


@dataclass
class NewsArticle:
    title: str
    description: str
    url: str
    source: str
    published_at: datetime
    symbol: Optional[str] = None
    sentiment: str = "neutral"
    sentiment_score: float = 0.0


class NewsFetcher:
    async def fetch_stock_news(self, symbol: str, max_articles: int = 10) -> List[NewsArticle]:
        try:
            yf_sym = f"{symbol}.NS" if not symbol.endswith(".NS") else symbol
            ticker = yf.Ticker(yf_sym)
            raw_news = await asyncio.to_thread(lambda: ticker.news)

            articles = []
            for item in raw_news[:max_articles]:
                content = item.get("content", {})
                title = content.get("title") or item.get("title") or ""
                summary = content.get("summary") or item.get("publisher") or ""
                url = content.get("canonicalUrl", {}).get("url") or item.get("link") or ""
                pub_time = item.get("providerPublishTime") or datetime.now().timestamp()

                if title:
                    articles.append(
                        NewsArticle(
                            title=title,
                            description=summary,
                            url=url,
                            source=item.get("publisher", "Yahoo Finance"),
                            published_at=datetime.fromtimestamp(pub_time),
                            symbol=symbol,
                        )
                    )
            return articles
        except Exception as exc:
            logger.error("Error fetching news for {}: {}", symbol, exc)
            return []


news_fetcher = NewsFetcher()
