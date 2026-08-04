"""Sentiment Analyzer module."""

from dataclasses import dataclass
from typing import List


@dataclass
class SentimentResult:
    sentiment: str
    score: float
    confidence: float
    positive_signals: List[str]
    negative_signals: List[str]
    summary: str


class SentimentAnalyzer:
    POS_WORDS = {
        "profit", "growth", "revenue", "beat", "strong", "upgrade", "buy",
        "record", "surge", "rally", "dividend", "order", "win", "bullish"
    }

    NEG_WORDS = {
        "loss", "decline", "fall", "drop", "weak", "downgrade", "sell",
        "miss", "plunge", "crash", "penalty", "lawsuit", "bearish", "debt"
    }

    def analyze_text(self, text: str) -> SentimentResult:
        words = set(text.lower().split())
        pos_found = list(words.intersection(self.POS_WORDS))
        neg_found = list(words.intersection(self.NEG_WORDS))

        pos_count = len(pos_found)
        neg_count = len(neg_found)

        if pos_count > neg_count:
            sentiment = "positive"
            score = min(1.0, 0.2 + 0.2 * (pos_count - neg_count))
        elif neg_count > pos_count:
            sentiment = "negative"
            score = max(-1.0, -0.2 - 0.2 * (neg_count - pos_count))
        else:
            sentiment = "neutral"
            score = 0.0

        return SentimentResult(
            sentiment=sentiment,
            score=score,
            confidence=70.0,
            positive_signals=[f"Positive keyword: {w}" for w in pos_found],
            negative_signals=[f"Negative keyword: {w}" for w in neg_found],
            summary=f"Sentiment is {sentiment} (Score: {score:.2f})",
        )

    def analyze_articles(self, articles: List) -> SentimentResult:
        if not articles:
            return SentimentResult("neutral", 0.0, 50.0, [], [], "No news available")

        total_score = 0.0
        pos_sigs = []
        neg_sigs = []

        for a in articles:
            text = f"{a.title} {a.description}"
            res = self.analyze_text(text)
            total_score += res.score
            pos_sigs.extend(res.positive_signals)
            neg_sigs.extend(res.negative_signals)

        avg_score = total_score / len(articles)
        sentiment = "positive" if avg_score > 0.15 else "negative" if avg_score < -0.15 else "neutral"

        return SentimentResult(
            sentiment=sentiment,
            score=round(avg_score, 2),
            confidence=75.0,
            positive_signals=list(set(pos_sigs)),
            negative_signals=list(set(neg_sigs)),
            summary=f"Overall news sentiment across {len(articles)} articles is {sentiment}.",
        )


sentiment_analyzer = SentimentAnalyzer()
