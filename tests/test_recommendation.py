"""Unit tests for Recommendation Engine."""

import pytest
from app.ranking.engine import recommendation_engine


@pytest.mark.asyncio
async def test_recommendation_engine():
    rec = await recommendation_engine.analyze_stock("RELIANCE", skip_ai=True)
    if rec:
        assert rec.symbol == "RELIANCE"
        assert rec.action in ["STRONG_BUY", "BUY", "WATCHLIST", "HOLD", "SELL", "STRONG_SELL"]
        assert 0.0 <= rec.confidence <= 100.0
        assert rec.entry_price > 0
        assert rec.stop_loss > 0
        assert rec.target_1 > 0
